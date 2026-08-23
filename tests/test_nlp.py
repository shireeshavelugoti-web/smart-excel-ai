import pytest
from backend.services.nlp_processor import parse_natural_instruction
from backend.services.column_matcher import match_column_name

def test_intent_classification_and_entities():
    # Prompt 1
    prompt1 = "Change the department of student 1025 to Artificial Intelligence."
    cols1 = ["Student ID", "Name", "Department", "GPA", "Email", "Phone"]
    res1 = parse_natural_instruction(prompt1, cols1)
    
    assert res1["intent"] == "UPDATE"
    assert res1["entities"]["matched_column"] == "Department"
    assert res1["entities"]["identifier"] == "1025"
    assert res1["entities"]["new_value"] == "Artificial Intelligence"
    assert res1["confidence"] >= 0.85

    # Prompt 2
    prompt2 = "Update the salary of employee E104 to 55000."
    cols2 = ["Employee ID", "Name", "Salary", "Department"]
    res2 = parse_natural_instruction(prompt2, cols2)
    assert res2["intent"] == "UPDATE"
    assert res2["entities"]["matched_column"] == "Salary"
    assert res2["entities"]["identifier"] == "E104"

    # Prompt 3: FIND
    prompt3 = "Find the employee with ID E105."
    res3 = parse_natural_instruction(prompt3)
    assert res3["intent"] == "FIND"
    assert res3["entities"]["identifier"] == "E105"

    # Prompt 4: CLEAN
    prompt4 = "Clean the customer data."
    res4 = parse_natural_instruction(prompt4)
    assert res4["intent"] == "CLEAN"

    # Prompt 5: PREDICT
    prompt5 = "Predict next month's sales."
    res5 = parse_natural_instruction(prompt5)
    assert res5["intent"] == "PREDICT"

    # Prompt 6: ADD Column
    prompt6 = "Add a column named Address with default N/A."
    res6 = parse_natural_instruction(prompt6, cols1)
    assert res6["intent"] == "ADD"
    assert res6["entities"]["target_type"] == "column"
    assert res6["entities"]["target_field_raw"] == "Address"

    # Prompt 7: ADD Row
    prompt7 = "Add new student 1031 with name John."
    res7 = parse_natural_instruction(prompt7, cols1)
    assert res7["intent"] == "ADD"
    assert res7["entities"]["target_type"] == "row"
    assert res7["entities"]["identifier"] == "1031"

    # Prompt 8: DELETE Column
    prompt8 = "Delete column Phone."
    res8 = parse_natural_instruction(prompt8, cols1)
    assert res8["intent"] == "DELETE"
    assert res8["entities"]["target_type"] == "column"
    assert res8["entities"]["matched_column"] == "Phone"

    # Prompt 9: DELETE Row
    prompt9 = "Delete student record 1025."
    res9 = parse_natural_instruction(prompt9, cols1)
    assert res9["intent"] == "DELETE"
    assert res9["entities"]["target_type"] == "row"
    assert res9["entities"]["identifier"] == "1025"

    # Prompt 10: BULK_UPDATE
    prompt10 = "Change the department of all ECE students to AI."
    res10 = parse_natural_instruction(prompt10, cols1)
    assert res10["intent"] == "BULK_UPDATE"
    assert res10["entities"]["matched_column"] == "Department"
    assert res10["entities"]["condition_value"] == "ECE"
    assert res10["entities"]["new_value"] == "AI"

    # Prompt 11: BULK_DELETE
    prompt11 = "Delete all rows where GPA is below 3.0"
    res11 = parse_natural_instruction(prompt11, cols1)
    assert res11["intent"] == "BULK_DELETE"
    assert res11["entities"]["condition_column"] == "GPA"
    assert res11["entities"]["operator_type"] == "<"
    assert res11["entities"]["condition_value"] == "3.0"

def test_fuzzy_column_matching():
    cols = ["Student_ID", "Student_Department", "Contact_Phone_Number", "Annual_Salary"]
    
    col, score = match_column_name("dept", cols)
    assert col == "Student_Department"
    
    col, score = match_column_name("phone", cols)
    assert col == "Contact_Phone_Number"
    
    col, score = match_column_name("salary", cols)
    assert col == "Annual_Salary"
