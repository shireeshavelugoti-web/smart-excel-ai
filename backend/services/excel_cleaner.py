import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from backend.services.excel_reader import load_sheet_dataframe, get_workbook_sheets
from backend.models.anomaly_detector import detect_outliers_isolation_forest
from backend.utils.file_handler import get_modified_file_path

def audit_dataset_issues(file_path: str, sheet_name: str = None) -> Dict[str, Any]:
    """
    Performs data quality checks across missing values, duplicates, spacing,
    capitalization inconsistencies, and Isolation Forest outliers.
    """
    df = load_sheet_dataframe(file_path, sheet_name)
    sheets = get_workbook_sheets(file_path)
    
    issues_list = []
    
    # 1. Missing Values
    missing_sum = df.isnull().sum()
    missing_cols = missing_sum[missing_sum > 0].to_dict()
    total_missing = int(missing_sum.sum())
    if total_missing > 0:
        issues_list.append({
            "type": "Missing Values",
            "count": total_missing,
            "details": f"Found missing values in {len(missing_cols)} columns: {', '.join(missing_cols.keys())}",
            "suggestion": "Impute numerical columns with median and categorical with mode."
        })

    # 2. Duplicate Rows
    duplicates_count = int(df.duplicated().sum())
    if duplicates_count > 0:
        issues_list.append({
            "type": "Duplicate Rows",
            "count": duplicates_count,
            "details": f"Found {duplicates_count} identical duplicate row(s).",
            "suggestion": "Deduplicate dataset keeping the first occurrence."
        })

    # 3. Extra Spaces (Leading / Trailing Whitespace)
    str_cols = df.select_dtypes(include=['object', 'string']).columns
    space_issue_count = 0
    for col in str_cols:
        col_space = df[col].astype(str).str.contains(r'^\s+|\s+$|\s{2,}', regex=True, na=False).sum()
        space_issue_count += int(col_space)
        
    if space_issue_count > 0:
        issues_list.append({
            "type": "Extra Spaces",
            "count": space_issue_count,
            "details": f"Found {space_issue_count} text cell(s) with leading, trailing, or double spaces.",
            "suggestion": "Strip whitespace and normalize internal spaces."
        })

    # 4. Inconsistent Capitalization
    cap_issues = 0
    for col in str_cols:
        vals = df[col].dropna().astype(str).unique()
        lower_map = {}
        for v in vals:
            v_low = v.strip().lower()
            if v_low in lower_map and lower_map[v_low] != v:
                cap_issues += 1
            else:
                lower_map[v_low] = v
                
    if cap_issues > 0:
        issues_list.append({
            "type": "Inconsistent Capitalization",
            "count": cap_issues,
            "details": f"Found {cap_issues} categorical column value(s) with mixed casing (e.g., 'cse' vs 'CSE').",
            "suggestion": "Standardize text columns to upper/title case."
        })

    # 5. Isolation Forest Outliers
    outliers = detect_outliers_isolation_forest(df)
    if outliers:
        issues_list.append({
            "type": "Numerical Outliers (Isolation Forest)",
            "count": len(outliers),
            "details": f"Isolation Forest flagged {len(outliers)} anomalous numerical record(s).",
            "suggestion": "Review or cap numerical extreme values."
        })

    return {
        "sheets": sheets,
        "selected_sheet": sheet_name or sheets[0],
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "total_issues_count": total_missing + duplicates_count + space_issue_count + cap_issues + len(outliers),
        "issues_summary": issues_list,
        "outlier_records": outliers[:5] # top 5 for preview
    }

def apply_dataset_cleaning(file_path: str, sheet_name: str = None, options: Dict[str, bool] = None) -> Tuple[str, str, Dict[str, Any]]:
    """
    Cleans dataset based on user-selected toggles and saves to a new file.
    Never overwrites the original file.
    """
    opts = options or {
        "fill_missing": True,
        "remove_duplicates": True,
        "trim_spaces": True,
        "standardize_case": True,
        "remove_outliers": False
    }
    
    df = load_sheet_dataframe(file_path, sheet_name)
    rows_before = len(df)
    
    # 1. Trim Spaces
    if opts.get("trim_spaces"):
        str_cols = df.select_dtypes(include=['object', 'string']).columns
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
            
    # 2. Standardize Casing
    if opts.get("standardize_case"):
        str_cols = df.select_dtypes(include=['object', 'string']).columns
        for col in str_cols:
            # Uppercase short codes like ID, CSE, AI, otherwise Title case
            df[col] = df[col].apply(lambda x: (str(x).upper() if len(str(x)) <= 3 else str(x).title()) if pd.notnull(x) else x)
            
    # 3. Remove Duplicates
    if opts.get("remove_duplicates"):
        df = df.drop_duplicates().reset_index(drop=True)
        
    # 4. Fill Missing Values
    if opts.get("fill_missing"):
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
                    df[col] = df[col].fillna(mode_val)

    # 5. Remove Outliers
    if opts.get("remove_outliers"):
        outliers = detect_outliers_isolation_forest(df)
        outlier_indices = [o["dataframe_index"] for o in outliers]
        df = df.drop(index=outlier_indices, errors="ignore").reset_index(drop=True)

    output_path, output_filename = get_modified_file_path(os.path.basename(file_path))
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".csv":
        df.to_csv(output_path, index=False)
    else:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name or "Sheet1", index=False)

    return output_path, output_filename, {
        "status": "success",
        "message": "Dataset cleaned successfully.",
        "rows_before": rows_before,
        "rows_after": len(df),
        "cleaned_filename": output_filename
    }
