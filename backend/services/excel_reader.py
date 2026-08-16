import os
import pandas as pd
import openpyxl
from typing import Dict, Any, List

def get_workbook_sheets(file_path: str) -> List[str]:
    """
    Returns sheet names for an Excel workbook or ['Sheet1'] for CSV files.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return ["Sheet1"]
    
    excel_file = pd.ExcelFile(file_path)
    return excel_file.sheet_names

def load_sheet_dataframe(file_path: str, sheet_name: str = None) -> pd.DataFrame:
    """
    Loads a sheet or CSV into a Pandas DataFrame.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    else:
        sheets = get_workbook_sheets(file_path)
        target_sheet = sheet_name if sheet_name and sheet_name in sheets else sheets[0]
        df = pd.read_excel(file_path, sheet_name=target_sheet)
    return df

def get_dataset_overview(file_path: str, sheet_name: str = None) -> Dict[str, Any]:
    """
    Returns comprehensive dataset overview stats for UI display.
    """
    df = load_sheet_dataframe(file_path, sheet_name)
    sheets = get_workbook_sheets(file_path)
    
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    
    missing_counts = df.isnull().sum().to_dict()
    total_missing = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    
    sample_rows = df.head(10).fillna("").to_dict(orient="records")
    
    return {
        "sheets": sheets,
        "selected_sheet": sheet_name or sheets[0],
        "rows": len(df),
        "columns": list(df.columns),
        "column_count": len(df.columns),
        "numerical_features": num_cols,
        "categorical_features": cat_cols,
        "total_missing": total_missing,
        "missing_per_column": missing_counts,
        "duplicate_rows": duplicate_rows,
        "sample_data": sample_rows
    }
