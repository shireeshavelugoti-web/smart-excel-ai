import os
import pandas as pd
from backend.services.excel_cleaner import audit_dataset_issues, apply_dataset_cleaning

SAMPLE_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.csv")

def test_data_cleaner_audit_and_apply(tmp_path):
    # Create dirty dataframe test file
    df_dirty = pd.DataFrame({
        "ID": [1, 2, 2, 4, 5, 6, 7, 8, 9, 10],
        "Department": [" CSE ", "cse", "cse", None, "ECE", "ME", "EEE", "AI", "AI", "AI"],
        "Salary": [50000, 52000, 52000, 48000, 51000, 49000, 53000, 50000, 51000, 999999] # 999999 outlier
    })
    test_file = os.path.join(tmp_path, "dirty_data.csv")
    df_dirty.to_csv(test_file, index=False)
    
    audit = audit_dataset_issues(test_file)
    assert audit["total_issues_count"] > 0
    
    output_path, output_filename, summary = apply_dataset_cleaning(test_file, options={
        "fill_missing": True,
        "remove_duplicates": True,
        "trim_spaces": True,
        "standardize_case": True,
        "remove_outliers": True
    })
    
    assert os.path.exists(output_path)
    df_clean = pd.read_csv(output_path)
    assert df_clean["Department"].isnull().sum() == 0
    assert df_clean.duplicated().sum() == 0
    assert len(df_clean) < len(df_dirty)
    assert "processed_sheets_data" in summary
    assert "Sheet1" in summary["processed_sheets_data"]
