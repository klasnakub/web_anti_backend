from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileUploadResponse(BaseModel):
    file_name: str
    file_url: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    bucket_path: str 