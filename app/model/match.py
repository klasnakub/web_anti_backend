from datetime import datetime
from pydantic import BaseModel, Field

class MatchRequest(BaseModel):
    match_id: int
    home_team: str
    away_team: str
    league_id: str
    match_date: datetime
    status: str

class MatchResponse(BaseModel):
    match_id: int
    home_team: str
    away_team: str
    match_date: datetime
    league_id: str
    league_name: str
    status: str