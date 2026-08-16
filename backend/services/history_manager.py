import os
import json
from datetime import datetime
from typing import List, Dict, Any

HISTORY_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "operation_history.json")

def get_history() -> List[Dict[str, Any]]:
    """
    Reads the operation history log.
    """
    if not os.path.exists(HISTORY_FILE_PATH):
        # Default seed history entries matching prompt example
        seed = [
            {
                "id": "hist_1",
                "date": "12 Aug 2026",
                "file": "Students.xlsx",
                "action": "UPDATE",
                "target": "Student 1025",
                "status": "Completed"
            },
            {
                "id": "hist_2",
                "date": "14 Aug 2026",
                "file": "Employees.xlsx",
                "action": "CLEAN",
                "target": "Missing & Duplicates",
                "status": "Completed"
            },
            {
                "id": "hist_3",
                "date": "15 Aug 2026",
                "file": "Real_Estate_Price_Prediction_Dataset.csv",
                "action": "PREDICT",
                "target": "Random Forest Model",
                "status": "Completed"
            }
        ]
        save_history(seed)
        return seed
        
    try:
        with open(HISTORY_FILE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history_list: List[Dict[str, Any]]):
    """
    Writes history list to disk.
    """
    try:
        with open(HISTORY_FILE_PATH, "w") as f:
            json.dump(history_list, f, indent=2)
    except Exception:
        pass

def add_history_entry(file_name: str, action: str, target: str, status: str = "Completed") -> Dict[str, Any]:
    """
    Appends a new operation record to history.
    """
    history = get_history()
    now_str = datetime.now().strftime("%d %b %Y, %H:%M")
    new_entry = {
        "id": f"hist_{len(history) + 1}",
        "date": now_str,
        "file": file_name,
        "action": action,
        "target": target,
        "status": status
    }
    history.insert(0, new_entry) # newest first
    save_history(history)
    return new_entry
