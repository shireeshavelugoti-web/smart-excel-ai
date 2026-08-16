import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.utils.validators import validate_excel_file, sanitize_instruction
from backend.utils.file_handler import save_uploaded_file, TEMP_DIR, OUTPUT_DIR, get_modified_file_path
from backend.services.excel_reader import get_workbook_sheets, get_dataset_overview, load_sheet_dataframe
from backend.services.nlp_processor import parse_natural_instruction
from backend.services.excel_updater import preview_excel_update, apply_excel_update
from backend.services.excel_cleaner import audit_dataset_issues, apply_dataset_cleaning
from backend.models.prediction_models import analyze_dataset_ml, train_ml_model, predict_sample
from backend.services.history_manager import get_history, add_history_entry

app = FastAPI(
    title="Smart Excel AI Automation Assistant API",
    description="Backend API powered by Python, Pandas, NLTK, and Scikit-Learn",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "online",
        "app_name": "Smart Excel AI Automation Assistant",
        "docs_url": "/docs"
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    is_valid, error = validate_excel_file(file.filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
        
    contents = await file.read()
    file_path = save_uploaded_file(contents, file.filename)
    overview = get_dataset_overview(file_path)
    
    return {
        "status": "uploaded",
        "file_path": file_path,
        "filename": file.filename,
        "overview": overview
    }

@app.post("/api/nlp/parse")
def nlp_parse(instruction: str = Body(..., embed=True), columns: List[str] = Body(None, embed=True)):
    clean_instr = sanitize_instruction(instruction)
    if not clean_instr:
        raise HTTPException(status_code=400, detail="Instruction cannot be empty.")
    res = parse_natural_instruction(clean_instr, columns)
    return res

@app.post("/api/excel/preview")
def excel_preview(
    file_path: str = Body(..., embed=True),
    instruction: str = Body(..., embed=True),
    sheet_name: Optional[str] = Body(None, embed=True)
):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File path not found.")
        
    preview = preview_excel_update(file_path, instruction, sheet_name)
    return preview

@app.post("/api/excel/apply")
def excel_apply(
    file_path: str = Body(..., embed=True),
    preview_data: Dict[str, Any] = Body(..., embed=True)
):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File path not found.")
        
    output_path, output_filename, summary = apply_excel_update(file_path, preview_data)
    
    # Record operation in history
    add_history_entry(
        file_name=os.path.basename(file_path),
        action="UPDATE",
        target=f"{preview_data.get('target_column')} = {preview_data.get('new_value')}",
        status="Completed"
    )
    
    return {
        "status": "success",
        "summary": summary,
        "download_url": f"/api/download/{output_filename}"
    }

@app.post("/api/cleaner/audit")
def cleaner_audit(
    file_path: str = Body(..., embed=True),
    sheet_name: Optional[str] = Body(None, embed=True)
):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File path not found.")
    res = audit_dataset_issues(file_path, sheet_name)
    return res

@app.post("/api/cleaner/apply")
def cleaner_apply(
    file_path: str = Body(..., embed=True),
    sheet_name: Optional[str] = Body(None, embed=True),
    options: Dict[str, bool] = Body(..., embed=True)
):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File path not found.")
        
    output_path, output_filename, summary = apply_dataset_cleaning(file_path, sheet_name, options)
    
    add_history_entry(
        file_name=os.path.basename(file_path),
        action="CLEAN",
        target="Missing, Duplicates & Outliers",
        status="Completed"
    )
    
    return {
        "status": "success",
        "summary": summary,
        "download_url": f"/api/download/{output_filename}"
    }

@app.post("/api/ml/analyze")
def ml_analyze(
    file_path: str = Body(..., embed=True),
    sheet_name: Optional[str] = Body(None, embed=True)
):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File path not found.")
        
    df = load_sheet_dataframe(file_path, sheet_name)
    res = analyze_dataset_ml(df)
    return res

@app.post("/api/ml/train")
def ml_train(
    file_path: str = Body(..., embed=True),
    target_column: str = Body(..., embed=True),
    model_name: str = Body("Random Forest", embed=True),
    sheet_name: Optional[str] = Body(None, embed=True)
):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File path not found.")
        
    df = load_sheet_dataframe(file_path, sheet_name)
    train_res = train_ml_model(df, target_column, model_name)
    
    add_history_entry(
        file_name=os.path.basename(file_path),
        action="TRAIN ML",
        target=f"{model_name} on {target_column}",
        status="Completed"
    )
    
    return train_res

@app.post("/api/ml/predict")
def ml_predict(
    model_id: str = Body(..., embed=True),
    input_features: Dict[str, Any] = Body(..., embed=True)
):
    res = predict_sample(model_id, input_features)
    
    add_history_entry(
        file_name="Dataset",
        action="PREDICT",
        target=f"Value: {res.get('prediction')}",
        status="Completed"
    )
    
    return res

@app.get("/api/history")
def history_list():
    return get_history()

@app.get("/api/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path=file_path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
