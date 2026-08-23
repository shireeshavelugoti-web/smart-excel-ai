import os
import pytest
from backend.services.excel_updater import preview_excel_update, apply_excel_update

SAMPLE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "Students.xlsx")

def test_excel_update_preview_and_apply():
    assert os.path.exists(SAMPLE_FILE), "Students.xlsx sample file must exist"
    
    instruction = "Change the department of student 1025 to Artificial Intelligence."
    preview = preview_excel_update(SAMPLE_FILE, instruction, "Students")
    
    assert preview["intent"] == "UPDATE"
    assert preview["target_column"] == "Department"
    assert preview["identifier"] == "1025"
    assert preview["new_value"] == "Artificial Intelligence"
    assert preview["old_value"] == "CSE"
    
    output_path, output_filename, summary = apply_excel_update(SAMPLE_FILE, preview)
    assert os.path.exists(output_path)
    assert output_filename != "Students.xlsx" # Ensure original file was NOT overwritten
    assert summary["status"] == "success"
    assert "processed_sheets_data" in summary
    assert "Students" in summary["processed_sheets_data"]

def test_excel_add_and_delete_preview_and_apply():
    # Test ADD Column
    preview_add_col = preview_excel_update(SAMPLE_FILE, "Add a column named Address", "Students")
    assert preview_add_col["intent"] == "ADD"
    assert preview_add_col["operation_type"] == "ADD_COLUMN"
    assert preview_add_col["target_column"] == "Address"
    out_path1, out_name1, sum1 = apply_excel_update(SAMPLE_FILE, preview_add_col)
    assert os.path.exists(out_path1)
    assert sum1["status"] == "success"

    # Test DELETE Column
    preview_del_col = preview_excel_update(SAMPLE_FILE, "Delete column Phone", "Students")
    assert preview_del_col["intent"] == "DELETE"
    assert preview_del_col["operation_type"] == "DELETE_COLUMN"
    assert preview_del_col["target_column"] == "Phone"
    out_path2, out_name2, sum2 = apply_excel_update(SAMPLE_FILE, preview_del_col)
    assert os.path.exists(out_path2)
    assert sum2["status"] == "success"

def test_excel_bulk_operations():
    # Bulk Update
    preview_bulk_up = preview_excel_update(SAMPLE_FILE, "Change the department of all ECE students to AI", "Students")
    assert preview_bulk_up["intent"] == "BULK_UPDATE"
    assert preview_bulk_up["operation_type"] == "BULK_UPDATE"
    assert preview_bulk_up["condition_value"] == "ECE"
    out_path1, out_name1, sum1 = apply_excel_update(SAMPLE_FILE, preview_bulk_up)
    assert os.path.exists(out_path1)
    assert sum1["status"] == "success"

    # Bulk Delete
    preview_bulk_del = preview_excel_update(SAMPLE_FILE, "Delete all rows where GPA is below 3.0", "Students")
    assert preview_bulk_del["intent"] == "BULK_DELETE"
    assert preview_bulk_del["operation_type"] == "BULK_DELETE"
    assert preview_bulk_del["operator_type"] == "<"
    out_path2, out_name2, sum2 = apply_excel_update(SAMPLE_FILE, preview_bulk_del)
    assert os.path.exists(out_path2)
    assert sum2["status"] == "success"
