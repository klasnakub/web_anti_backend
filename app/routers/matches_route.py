from fastapi import APIRouter, Depends
from model.match import MatchRequest, MatchResponse
from common import match_svc
from core.security import verify_token

router = APIRouter(tags=['matches'])

def is_ready():
    if match_svc:
        return True
    else:
        print(__name__, "Error: league_svc is not set. Please check your configuration.")
        return False

#@router.post("/matches", response_model=MatchResponse)
@router.post("/matches")
async def add_match(match_request: MatchRequest, payload: dict = Depends(verify_token)):
    """Add a new match"""
    return match_svc.add_match(match_request)

@router.get("/matches", response_model=list[MatchResponse])
async def list_matches(payload: dict = Depends(verify_token)):
    """List all matches"""
    return match_svc.list_all_matches()

@router.get("/matches/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, payload: dict = Depends(verify_token)):
    """Get a match"""
    return match_svc.get_match(match_id)

@router.delete("/matches/{match_id}")
async def delete_match(match_id: int, payload: dict = Depends(verify_token)):
    """Delete a match by match_id"""
    return match_svc.delete_match(match_id)

@router.put("/matches/{match_id}")
async def update_match(match_id: int, match_request: MatchRequest, payload: dict = Depends(verify_token)):
    """Update a match by match_id"""
    return match_svc.update_match(match_id, match_request)
