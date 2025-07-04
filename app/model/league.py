from datetime import datetime
from pydantic import BaseModel

class LeagueRequest(BaseModel):
    league_name: str
    country: str
    season: str
    status: str

class LeagueResponse(BaseModel):
    league_id: str
    league_name: str
    country: str
    season: str
    status: str
    created_at: datetime
    updated_at: datetime

