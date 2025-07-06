from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UrlSubmissionRequest(BaseModel):
    url: str
    type: Optional[str] = None
    league_id: Optional[str] = None
    match_id: Optional[str] = None
    status: Optional[str] = None
    image_file_name: Optional[str] = None

class UrlSubmissionResponse(BaseModel):
    submission_id: str
    url: str
    type: Optional[str] = None
    league_id: Optional[str] = None
    match_id: Optional[str] = None
    status: Optional[str] = None
    image_file_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    league_name: Optional[str] = None
    matches_name: Optional[str] = None 