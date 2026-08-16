import os
from typing import Tuple, Optional

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

def validate_excel_file(filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validates that the file has an allowed spreadsheet extension (.xlsx, .xls, .csv).
    """
    if not filename:
        return False, "Filename cannot be empty."
    
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, None

def sanitize_instruction(instruction: str) -> str:
    """
    Cleans and normalizes natural language instructions.
    """
    if not instruction:
        return ""
    return instruction.strip()
