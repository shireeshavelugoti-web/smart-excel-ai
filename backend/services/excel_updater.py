import os
import openpyxl
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from backend.services.excel_reader import load_sheet_dataframe, get_workbook_sheets
from backend.services.nlp_processor import parse_natural_instruction
from backend.utils.file_handler import get_modified_file_path

def preview_excel_update(file_path: str, instruction: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes natural language instruction and target file to produce an update preview
    without writing any changes to disk yet.
    """
    sheets = get_workbook_sheets(file_path)
    target_sheet = sheet_name if sheet_name and sheet_name in sheets else sheets[0]
    
    df = load_sheet_dataframe(file_path, target_sheet)
    available_cols = list(df.columns)
    
    parsed = parse_natural_instruction(instruction, available_cols)
    intent = parsed["intent"]
    entities = parsed["entities"]
    
    matched_col = entities["matched_column"] or (available_cols[0] if available_cols else None)
    identifier = entities["identifier"]
    new_value = entities["new_value"]
    
    target_row_idx = None
    old_value = None
    id_col_found = None
    
    # Locate row by matching identifier in any column
    if identifier:
        id_str = str(identifier).strip().lower()
        for col in df.columns:
            # check string matches
            matches = df[df[col].astype(str).str.strip().str.lower() == id_str]
            if not matches.empty:
                target_row_idx = int(matches.index[0])
                id_col_found = col
                break
                
    if target_row_idx is not None and matched_col in df.columns:
        old_value = str(df.at[target_row_idx, matched_col])
    else:
        # Fallback to row 0 if row not specified or found
        target_row_idx = 0
        old_value = str(df.at[0, matched_col]) if matched_col in df.columns else "N/A"
        
    return {
        "status": "preview_ready",
        "intent": intent,
        "raw_instruction": instruction,
        "target_sheet": target_sheet,
        "target_column": matched_col,
        "identifier": identifier,
        "id_column": id_col_found,
        "target_row_index": target_row_idx + 1 if target_row_idx is not None else 1, # 1-indexed row number for user
        "dataframe_row_index": target_row_idx,
        "old_value": old_value,
        "new_value": new_value if new_value is not None else "Updated Value",
        "confidence": parsed["confidence"]
    }

def apply_excel_update(file_path: str, preview_data: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
    """
    Applies confirmed changes to a new Excel file.
    Original uploaded file is NEVER overwritten.
    Returns (modified_file_path, output_filename, result_summary).
    """
    output_path, output_filename = get_modified_file_path(os.path.basename(file_path))
    ext = os.path.splitext(file_path)[1].lower()
    
    target_sheet = preview_data.get("target_sheet")
    target_col = preview_data.get("target_column")
    df_row_idx = preview_data.get("dataframe_row_index", 0)
    new_val = preview_data.get("new_value")
    
    if ext == ".csv":
        df = pd.read_csv(file_path)
        if target_col in df.columns and df_row_idx in df.index:
            df.at[df_row_idx, target_col] = new_val
        df.to_csv(output_path, index=False)
    else:
        wb = openpyxl.load_workbook(file_path)
        sheet_names = wb.sheetnames
        ws_name = target_sheet if target_sheet in sheet_names else sheet_names[0]
        ws = wb[ws_name]
        
        # Find column header index (1-based)
        col_idx = None
        for c in range(1, ws.max_column + 1):
            cell_val = str(ws.cell(row=1, column=c).value or "").strip()
            if cell_val.lower() == str(target_col).lower():
                col_idx = c
                break
                
        # OpenPyXL rows are 1-based header + 1
        openpyxl_row = df_row_idx + 2
        
        if col_idx:
            ws.cell(row=openpyxl_row, column=col_idx, value=new_val)
        else:
            # Fallback using pandas
            df = pd.read_excel(file_path, sheet_name=ws_name)
            if target_col in df.columns:
                df.at[df_row_idx, target_col] = new_val
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=ws_name, index=False)
            wb.close()
            return output_path, output_filename, {
                "status": "success",
                "message": "Update completed successfully.",
                "output_filename": output_filename
            }
            
        wb.save(output_path)
        wb.close()

    return output_path, output_filename, {
        "status": "success",
        "message": "Update completed successfully.",
        "output_filename": output_filename,
        "updated_cell": {
            "sheet": target_sheet,
            "column": target_col,
            "row": df_row_idx + 2,
            "old_value": preview_data.get("old_value"),
            "new_value": new_val
        }
    }
