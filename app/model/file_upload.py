from pydantic import BaseModel
from datetime import datetime

class FileUploadResponse(BaseModel):
    file_name: str
    file_url: str
    file_size: int
    content_type: str
    uploaded_at: datetime

class FileUploadInternal(BaseModel):
    file_name: str
    orig_file_name: str = ""
    file_url: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    submission_id: str
    bucket_path: str 