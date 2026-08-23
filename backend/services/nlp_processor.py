import re
from typing import Dict, Any, List, Optional
from backend.models.intent_classifier import intent_classifier_instance
from backend.services.column_matcher import match_column_name

def parse_natural_instruction(instruction: str, available_columns: List[str] = None) -> Dict[str, Any]:
    """
    Parses a natural language instruction into structured intent & entities.
    Examples:
      - "Change the department of student 1025 to Artificial Intelligence."
      - "Add a column named Address with default N/A."
      - "Add new student 1031 with name John."
      - "Delete column Phone."
      - "Delete student record 1025."
    """
    instruction_clean = instruction.strip()
    intent, confidence = intent_classifier_instance.predict(instruction_clean)
    
    extracted_target_field = None
    extracted_identifier = None
    extracted_new_value = None
    target_type = "cell" # "cell", "row", or "column"
    matched_column = None
    col_confidence = 0.0
    
    if intent == "UPDATE":
        target_type = "cell"
        # Regular expressions for update pattern:
        p1 = re.search(r'(?:change|update|set|modify)\s+(?:the\s+)?([a-zA-Z\s_]+?)\s+of\s+(?:student|employee|id|record|user|row)?\s*([a-zA-Z0-9_-]+)\s+to\s+(.+)', instruction_clean, re.IGNORECASE)
        p2 = re.search(r'(?:change|update|set|modify)\s+(?:the\s+)?([a-zA-Z\s_]+?)\s+to\s+(.+?)\s+for\s+(?:student|employee|id|record|user)?\s*([a-zA-Z0-9_-]+)', instruction_clean, re.IGNORECASE)
        p3 = re.search(r'(?:set|update)\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z\s_]+?)\s*=\s*(.+)', instruction_clean, re.IGNORECASE)

        if p1:
            extracted_target_field = p1.group(1).strip()
            extracted_identifier = p1.group(2).strip()
            extracted_new_value = p1.group(3).strip().rstrip('.')
        elif p2:
            extracted_target_field = p2.group(1).strip()
            extracted_new_value = p2.group(2).strip()
            extracted_identifier = p2.group(3).strip().rstrip('.')
        elif p3:
            extracted_identifier = p3.group(1).strip()
            extracted_target_field = p3.group(2).strip()
            extracted_new_value = p3.group(3).strip().rstrip('.')
        else:
            words = instruction_clean.split()
            ids = [w.strip('.,') for w in words if re.match(r'^[A-Za-z0-9_-]{2,}$', w) and w.lower() not in ["change", "update", "the", "department", "salary", "phone", "number", "student", "employee", "to", "for", "set", "of", "with"]]
            if ids:
                extracted_identifier = ids[0]
            if " to " in instruction_clean.lower():
                parts = instruction_clean.lower().split(" to ")
                extracted_new_value = parts[-1].strip().rstrip('.')

    elif intent == "ADD":
        p_add_col = re.search(r'(?:add|insert|create)\s+(?:a\s+)?column\s+(?:named\s+|called\s+)?([a-zA-Z0-9_\s]+?)(?:\s+with\s+default\s+(.+))?$', instruction_clean, re.IGNORECASE)
        p_add_col2 = re.search(r'(?:add|insert|create)\s+([a-zA-Z0-9_\s]+?)\s+column', instruction_clean, re.IGNORECASE)
        
        if p_add_col:
            target_type = "column"
            extracted_target_field = p_add_col.group(1).strip()
            if p_add_col.group(2):
                extracted_new_value = p_add_col.group(2).strip()
        elif p_add_col2:
            target_type = "column"
            extracted_target_field = p_add_col2.group(1).strip()
        else:
            target_type = "row"
            p_add_row = re.search(r'(?:add|insert)\s+(?:new\s+)?(?:\b(?:student|employee|user|record|row|with|id)\b\s*)*([a-zA-Z0-9_-]+)?(?:\s+(?:named|with name|department|with)\s+(.+))?', instruction_clean, re.IGNORECASE)
            if p_add_row and p_add_row.group(1):
                extracted_identifier = p_add_row.group(1).strip()
                extracted_new_value = p_add_row.group(2).strip() if p_add_row.group(2) else None
            else:
                words = instruction_clean.split()
                ids = [w.strip('.,') for w in words if re.match(r'^[A-Za-z0-9_-]{2,}$', w) and w.lower() not in ["add", "insert", "new", "row", "record", "student", "employee", "user", "with", "to", "for", "a"]]
                if ids:
                    extracted_identifier = ids[0]

    elif intent == "DELETE":
        p_del_col = re.search(r'(?:delete|remove|drop)\s+(?:the\s+)?column\s+([a-zA-Z0-9_\s]+)', instruction_clean, re.IGNORECASE)
        p_del_col2 = re.search(r'(?:delete|remove|drop)\s+([a-zA-Z0-9_\s]+?)\s+column', instruction_clean, re.IGNORECASE)
        
        if p_del_col:
            target_type = "column"
            extracted_target_field = p_del_col.group(1).strip().rstrip('.')
        elif p_del_col2:
            target_type = "column"
            extracted_target_field = p_del_col2.group(1).strip().rstrip('.')
        else:
            target_type = "row"
            p_del_row = re.search(r'(?:delete|remove|erase|drop)\s+(?:the\s+)?(?:\b(?:student|employee|user|record|row|with|id)\b\s*)*([a-zA-Z0-9_-]+)', instruction_clean, re.IGNORECASE)
            if p_del_row and p_del_row.group(1):
                extracted_identifier = p_del_row.group(1).strip().rstrip('.')
            else:
                words = instruction_clean.split()
                ids = [w.strip('.,') for w in words if re.match(r'^[A-Za-z0-9_-]{2,}$', w) and w.lower() not in ["delete", "remove", "erase", "drop", "the", "row", "record", "student", "employee", "user", "for"]]
                if ids:
                    extracted_identifier = ids[0]
                
    elif intent == "FIND":
        p_find = re.search(r'(?:find|search|locate|show)\s+(?:the\s+)?(?:employee|student|user|record)?\s*(?:with\s+id|id)?\s*([a-zA-Z0-9_-]+)', instruction_clean, re.IGNORECASE)
        if p_find:
            extracted_identifier = p_find.group(1).strip()

    # Column Matching if columns provided
    if available_columns and extracted_target_field:
        matched_column, col_confidence = match_column_name(extracted_target_field, available_columns)
    elif available_columns:
        for col in available_columns:
            if str(col).lower() in instruction_clean.lower():
                matched_column = col
                col_confidence = 0.90
                break

    final_confidence = min(confidence, col_confidence) if col_confidence > 0 else confidence

    return {
        "raw_instruction": instruction,
        "intent": intent,
        "confidence": round(final_confidence, 2),
        "entities": {
            "target_type": target_type,
            "target_field_raw": extracted_target_field,
            "matched_column": matched_column or extracted_target_field,
            "identifier": extracted_identifier,
            "new_value": extracted_new_value
        }
    }
