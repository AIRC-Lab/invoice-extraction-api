from pydantic import BaseModel
from typing import Dict, Any, Optional

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    filename: Optional[str] = None

class ExtractionResult(BaseModel):
    filename: str
    extracted_data: Dict[str, Any]
    status: str

