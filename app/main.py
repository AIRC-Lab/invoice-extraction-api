from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from worker.invoice_celery_app import invoice_celery_app, extract_invoice_task
from app.schemas import TaskStatus

app = FastAPI(title="Invoice Extraction API")

@app.post("/extract-invoice", response_model=List[TaskStatus])
async def extract_invoice(files: List[UploadFile] = File(...)):
    tasks = []
    for file in files:
        contents = await file.read()
        task = extract_invoice_task.delay(contents, file.filename)
        tasks.append({"task_id": task.id, "status": "PENDING", "filename": file.filename})
    return JSONResponse(content=tasks)

@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    task = invoice_celery_app.AsyncResult(task_id)
    response_data: Dict[str, Any] = {"task_id": task.id, "status": task.state}

    filename_from_args = None
    if task.args and len(task.args) > 1:
        filename_from_args = task.args[1]

    if task.state == 'PENDING':
        response_data["filename"] = filename_from_args
        response_data["result"] = None
    elif task.state == 'PROGRESS':
        response_data["filename"] = task.info.get('filename', filename_from_args)
        response_data["result"] = task.info.get('extracted_data')
    elif task.state == 'SUCCESS':
        response_data["filename"] = task.info.get('filename', filename_from_args)
        response_data["result"] = task.result
    elif task.state == 'FAILURE':
        # Retrieve detailed error information from task.info
        error_info = task.info if task.info and isinstance(task.info, dict) else {}
        response_data["filename"] = error_info.get('filename', filename_from_args)
        response_data["result"] = {
            "error_type": error_info.get('error_type', 'UnknownError'),
            "error_message": error_info.get('error_message', str(task.result)),
            "traceback": error_info.get('traceback', 'No traceback available')
        }
    else:
        response_data["filename"] = filename_from_args
        response_data["result"] = None
    
    return JSONResponse(content=response_data)