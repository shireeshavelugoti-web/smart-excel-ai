import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from backend.services.excel_reader import load_sheet_dataframe, get_workbook_sheets
from backend.models.anomaly_detector import detect_outliers_isolation_forest
from backend.utils.file_handler import get_modified_file_path

def audit_dataset_issues(file_path: str, sheet_name: str = None) -> Dict[str, Any]:
    """
    Performs comprehensive data quality checks across missing values, duplicates, spacing,
    capitalization inconsistencies, invalid emails/phones, empty rows/cols, and Isolation Forest outliers.
    """
    df = load_sheet_dataframe(file_path, sheet_name)
    sheets = get_workbook_sheets(file_path)
    
    issues_list = []
    recommendations = []
    
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols if total_rows and total_cols else 1

    # 1. Missing Values
    missing_sum = df.isnull().sum()
    missing_cols = missing_sum[missing_sum > 0].to_dict()
    total_missing = int(missing_sum.sum())
    if total_missing > 0:
        issues_list.append({
            "type": "Missing Values",
            "count": total_missing,
            "details": f"Found missing values in {len(missing_cols)} column(s): {', '.join(missing_cols.keys())}",
            "suggestion": "Impute numerical columns with median and categorical with mode."
        })
        recommendations.append({
            "id": "fill_missing",
            "category": "Missing Data",
            "title": f"Fill {total_missing} missing value(s)",
            "description": "Automatically fill missing numeric values with median and text fields with mode.",
            "confidence": 0.95,
            "action_key": "fill_missing"
        })

    # 2. Duplicate Rows & Duplicate IDs
    duplicates_count = int(df.duplicated().sum())
    if duplicates_count > 0:
        issues_list.append({
            "type": "Duplicate Rows",
            "count": duplicates_count,
            "details": f"Found {duplicates_count} identical duplicate row(s).",
            "suggestion": "Deduplicate dataset keeping the first occurrence."
        })
        recommendations.append({
            "id": "remove_duplicates",
            "category": "Duplicates",
            "title": f"Remove {duplicates_count} duplicate row(s)",
            "description": "Drop redundant duplicate rows to preserve data integrity.",
            "confidence": 0.98,
            "action_key": "remove_duplicates"
        })

    # 3. Invalid Emails & Phone Numbers
    invalid_emails = 0
    invalid_phones = 0
    str_cols = df.select_dtypes(include=['object', 'string']).columns

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    for col in str_cols:
        col_l = str(col).lower()
        if "email" in col_l or df[col].astype(str).str.contains("@").any():
            invalid_mask = df[col].dropna().astype(str).apply(lambda x: not bool(re.match(email_regex, x.strip())))
            invalid_emails += int(invalid_mask.sum())
        if "phone" in col_l or "mobile" in col_l:
            invalid_phone_mask = df[col].dropna().astype(str).apply(lambda x: not (x.replace("-","").replace("+","").replace(" ","").isdigit() and len(x.replace("-","").replace("+","").replace(" ","")) >= 7))
            invalid_phones += int(invalid_phone_mask.sum())

    if invalid_emails > 0:
        issues_list.append({
            "type": "Invalid Email Formats",
            "count": invalid_emails,
            "details": f"Found {invalid_emails} invalid email format(s).",
            "suggestion": "Flag or sanitize malformed email addresses."
        })
        recommendations.append({
            "id": "fix_invalid_emails",
            "category": "Format Validation",
            "title": f"Sanitize {invalid_emails} invalid email(s)",
            "description": "Standardize email formatting and flag malformed domains.",
            "confidence": 0.91,
            "action_key": "fix_invalid_emails"
        })

    if invalid_phones > 0:
        issues_list.append({
            "type": "Invalid Phone Formats",
            "count": invalid_phones,
            "details": f"Found {invalid_phones} non-standard phone number(s).",
            "suggestion": "Normalize phone numbers to standard 10-digit digits."
        })

    # 4. Extra Spaces (Leading / Trailing Whitespace)
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
        recommendations.append({
            "id": "trim_spaces",
            "category": "Text Normalization",
            "title": f"Trim extra spaces in {space_issue_count} text cell(s)",
            "description": "Clean leading, trailing, and redundant internal whitespace.",
            "confidence": 0.99,
            "action_key": "trim_spaces"
        })

    # 5. Inconsistent Capitalization
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
        recommendations.append({
            "id": "standardize_case",
            "category": "Casing Normalization",
            "title": f"Standardize capitalization across text fields",
            "description": "Convert acronyms to uppercase and words to proper title casing.",
            "confidence": 0.96,
            "action_key": "standardize_case"
        })

    # 6. Isolation Forest Outliers
    outliers = detect_outliers_isolation_forest(df)
    if outliers:
        issues_list.append({
            "type": "Numerical Outliers (Isolation Forest)",
            "count": len(outliers),
            "details": f"Isolation Forest flagged {len(outliers)} anomalous numerical record(s).",
            "suggestion": "Review or remove extreme statistical outliers."
        })
        recommendations.append({
            "id": "remove_outliers",
            "category": "Anomaly Detection",
            "title": f"Remove {len(outliers)} ML anomaly outlier(s)",
            "description": "Filter out extreme anomalous records detected by Isolation Forest.",
            "confidence": 0.88,
            "action_key": "remove_outliers"
        })

    total_issues = total_missing + duplicates_count + invalid_emails + invalid_phones + space_issue_count + cap_issues + len(outliers)
    quality_score = max(5.0, min(100.0, round((1.0 - (total_issues / max(total_cells, 1))) * 100, 1)))

    return {
        "sheets": sheets,
        "selected_sheet": sheet_name or sheets[0],
        "total_rows": total_rows,
        "total_columns": total_cols,
        "total_issues_count": total_issues,
        "missing_values_count": total_missing,
        "duplicates_count": duplicates_count,
        "invalid_emails_count": invalid_emails,
        "invalid_phones_count": invalid_phones,
        "quality_score": quality_score,
        "issues_summary": issues_list,
        "recommendations": recommendations,
        "outlier_records": outliers[:5]
    }

import re

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
        "remove_outliers": False,
        "fix_invalid_emails": True
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

    # 5. Fix Invalid Emails
    if opts.get("fix_invalid_emails"):
        str_cols = df.select_dtypes(include=['object', 'string']).columns
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        for col in str_cols:
            if "email" in str(col).lower():
                df[col] = df[col].apply(lambda x: x if pd.isnull(x) or bool(re.match(email_regex, str(x).strip())) else f"{str(x).strip().lower()}@domain.com")

    # 6. Remove Outliers
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

    # Read back final modified data directly from processed workbook file on disk
    processed_sheets_data = {}
    try:
        if ext == ".csv":
            final_df = pd.read_csv(output_path)
            processed_sheets_data["Sheet1"] = final_df.fillna("").to_dict(orient="records")
        else:
            xls = pd.ExcelFile(output_path)
            for s_name in xls.sheet_names:
                sheet_df = pd.read_excel(xls, sheet_name=s_name)
                processed_sheets_data[s_name] = sheet_df.fillna("").to_dict(orient="records")
    except Exception as e:
        processed_sheets_data[sheet_name or "Sheet1"] = df.fillna("").to_dict(orient="records")

    return output_path, output_filename, {
        "status": "success",
        "message": "Dataset cleaned successfully.",
        "rows_before": rows_before,
        "rows_after": len(df),
        "cleaned_filename": output_filename,
        "sheet_names": list(processed_sheets_data.keys()),
        "processed_sheets_data": processed_sheets_data
    }
