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

def test_fuzzy_column_matching():
    cols = ["Student_ID", "Student_Department", "Contact_Phone_Number", "Annual_Salary"]
    
    col, score = match_column_name("dept", cols)
    assert col == "Student_Department"
    
    col, score = match_column_name("phone", cols)
    assert col == "Contact_Phone_Number"
    
    col, score = match_column_name("salary", cols)
    assert col == "Annual_Salary"
