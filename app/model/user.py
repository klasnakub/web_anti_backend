from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
