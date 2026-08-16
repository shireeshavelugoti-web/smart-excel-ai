import os
import uuid
import shutil
from typing import Tuple

TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp_uploads")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temp_outputs")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_uploaded_file(file_bytes: bytes, original_filename: str) -> str:
    """
    Saves uploaded file bytes to a temporary directory with a unique ID to prevent collisions.
    Never overwrites original files.
    """
    ext = os.path.splitext(original_filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = os.path.join(TEMP_DIR, unique_filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path

def get_modified_file_path(original_filename: str) -> Tuple[str, str]:
    """
    Generates a separate destination path for modified files without overwriting the original.
    Returns (full_path, output_filename).
    """
    name, ext = os.path.splitext(original_filename)
    output_filename = f"{name}_modified_{uuid.uuid4().hex[:6]}{ext}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    return output_path, output_filename

def cleanup_file(file_path: str):
    """
    Removes temporary file if exists.
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
