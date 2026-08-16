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
