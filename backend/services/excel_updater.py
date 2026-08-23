import os
import openpyxl
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from backend.services.excel_reader import load_sheet_dataframe, get_workbook_sheets
from backend.services.nlp_processor import parse_natural_instruction
from backend.utils.file_handler import get_modified_file_path

def preview_excel_update(file_path: str, instruction: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes natural language instruction and target file to produce an update, add, or delete preview
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
    target_type = entities.get("target_type", "cell")
    
    target_row_idx = None
    old_value = None
    id_col_found = None
    operation_type = intent
    
    if intent == "ADD":
        if target_type == "column":
            operation_type = "ADD_COLUMN"
            col_to_add = entities["target_field_raw"] or "New_Column"
            return {
                "status": "preview_ready",
                "intent": intent,
                "operation_type": operation_type,
                "raw_instruction": instruction,
                "target_sheet": target_sheet,
                "target_column": col_to_add,
                "default_value": new_value if new_value else "N/A",
                "confidence": parsed["confidence"]
            }
        else:
            operation_type = "ADD_ROW"
            new_id = identifier or f"ID_{len(df) + 1001}"
            return {
                "status": "preview_ready",
                "intent": intent,
                "operation_type": operation_type,
                "raw_instruction": instruction,
                "target_sheet": target_sheet,
                "identifier": new_id,
                "target_row_index": len(df) + 1,
                "dataframe_row_index": len(df),
                "new_value": new_value if new_value else f"New Record ({new_id})",
                "confidence": parsed["confidence"]
            }
            
    elif intent == "DELETE":
        if target_type == "column":
            operation_type = "DELETE_COLUMN"
            return {
                "status": "preview_ready",
                "intent": intent,
                "operation_type": operation_type,
                "raw_instruction": instruction,
                "target_sheet": target_sheet,
                "target_column": matched_col,
                "confidence": parsed["confidence"]
            }
        else:
            operation_type = "DELETE_ROW"
            if identifier:
                id_str = str(identifier).strip().lower()
                for col in df.columns:
                    matches = df[df[col].astype(str).str.strip().str.lower() == id_str]
                    if not matches.empty:
                        target_row_idx = int(matches.index[0])
                        id_col_found = col
                        break
            if target_row_idx is None:
                target_row_idx = 0
            
            row_summary = str(df.iloc[target_row_idx].to_dict()) if not df.empty else "N/A"
            return {
                "status": "preview_ready",
                "intent": intent,
                "operation_type": operation_type,
                "raw_instruction": instruction,
                "target_sheet": target_sheet,
                "identifier": identifier,
                "id_column": id_col_found,
                "target_row_index": target_row_idx + 1 if target_row_idx is not None else 1,
                "dataframe_row_index": target_row_idx,
                "deleted_row_preview": row_summary,
                "confidence": parsed["confidence"]
            }
            
    else: # UPDATE
        operation_type = "UPDATE"
        if identifier:
            id_str = str(identifier).strip().lower()
            for col in df.columns:
                matches = df[df[col].astype(str).str.strip().str.lower() == id_str]
                if not matches.empty:
                    target_row_idx = int(matches.index[0])
                    id_col_found = col
                    break
                    
        if target_row_idx is not None and matched_col in df.columns:
            old_value = str(df.at[target_row_idx, matched_col])
        else:
            target_row_idx = 0
            old_value = str(df.at[0, matched_col]) if matched_col in df.columns else "N/A"
            
        return {
            "status": "preview_ready",
            "intent": intent,
            "operation_type": operation_type,
            "raw_instruction": instruction,
            "target_sheet": target_sheet,
            "target_column": matched_col,
            "identifier": identifier,
            "id_column": id_col_found,
            "target_row_index": target_row_idx + 1 if target_row_idx is not None else 1,
            "dataframe_row_index": target_row_idx,
            "old_value": old_value,
            "new_value": new_value if new_value is not None else "Updated Value",
            "confidence": parsed["confidence"]
        }

def apply_excel_update(file_path: str, preview_data: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
    """
    Applies confirmed changes (Update, Add, Delete) to a new Excel/CSV file.
    Original uploaded file is NEVER overwritten.
    Returns (modified_file_path, output_filename, result_summary).
    """
    output_path, output_filename = get_modified_file_path(os.path.basename(file_path))
    ext = os.path.splitext(file_path)[1].lower()
    
    target_sheet = preview_data.get("target_sheet")
    op_type = preview_data.get("operation_type", preview_data.get("intent", "UPDATE"))
    target_col = preview_data.get("target_column")
    df_row_idx = preview_data.get("dataframe_row_index", 0)
    new_val = preview_data.get("new_value")
    identifier = preview_data.get("identifier")
    
    # Load DataFrame
    if ext == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = load_sheet_dataframe(file_path, target_sheet)
        
    summary_msg = "Operation completed successfully."
    
    if op_type == "ADD_COLUMN":
        col_name = target_col or "New_Column"
        default_v = preview_data.get("default_value", "N/A")
        df[col_name] = default_v
        summary_msg = f"Added column '{col_name}' with default value '{default_v}'."
        
    elif op_type == "ADD_ROW":
        new_row = {}
        for col in df.columns:
            col_l = str(col).lower()
            if "id" in col_l and identifier:
                new_row[col] = identifier
            elif "name" in col_l and new_val:
                new_row[col] = new_val
            elif "dept" in col_l and new_val and ("cse" in str(new_val).lower() or "ai" in str(new_val).lower()):
                new_row[col] = new_val
            else:
                new_row[col] = "N/A"
        df.loc[len(df)] = new_row
        summary_msg = f"Added new row (Record ID: {identifier or len(df)})."
        
    elif op_type == "DELETE_COLUMN":
        if target_col in df.columns:
            df = df.drop(columns=[target_col])
            summary_msg = f"Deleted column '{target_col}'."
        else:
            summary_msg = f"Column '{target_col}' not found."
            
    elif op_type == "DELETE_ROW":
        if df_row_idx in df.index:
            df = df.drop(index=df_row_idx).reset_index(drop=True)
            summary_msg = f"Deleted row #{df_row_idx + 1}."
        else:
            summary_msg = f"Row index #{df_row_idx + 1} out of bounds."
            
    else: # UPDATE
        if target_col in df.columns and df_row_idx in df.index:
            df.at[df_row_idx, target_col] = new_val
            summary_msg = f"Updated cell at row {df_row_idx + 1}, column '{target_col}'."

    # Save modified DataFrame
    if ext == ".csv":
        df.to_csv(output_path, index=False)
    else:
        # Preserve original workbook sheets if multi-sheet Excel file
        try:
            wb = openpyxl.load_workbook(file_path)
            sheet_names = wb.sheetnames
            ws_name = target_sheet if target_sheet in sheet_names else sheet_names[0]
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Write modified target sheet
                df.to_excel(writer, sheet_name=ws_name, index=False)
                # Copy remaining sheets unchanged
                for s in sheet_names:
                    if s != ws_name:
                        df_other = pd.read_excel(file_path, sheet_name=s)
                        df_other.to_excel(writer, sheet_name=s, index=False)
            wb.close()
        except Exception:
            df.to_excel(output_path, index=False)

    return output_path, output_filename, {
        "status": "success",
        "operation_type": op_type,
        "message": summary_msg,
        "output_filename": output_filename
    }
