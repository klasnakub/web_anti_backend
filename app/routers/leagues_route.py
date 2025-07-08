from fastapi import APIRouter, Depends
from model.league import LeagueRequest, LeagueResponse
from common import league_svc
from core.security import verify_token

router = APIRouter(tags=['leagues'])

def is_ready():
    if league_svc:
        return True
    else:
        print(__name__, "Error: league_svc is not set. Please check your configuration.")
        return False

@router.post("/leagues", response_model=LeagueResponse)
async def add_league(league_request: LeagueRequest, payload: dict = Depends(verify_token)):
    """Add a new league"""
    return league_svc.add_league_to_database(league_request)

@router.get("/leagues", response_model=list[LeagueResponse])
async def list_leagues(payload: dict = Depends(verify_token)):
    """List all leagues"""
    return league_svc.list_all_leagues()

@router.get("/leagues/{league_id}", response_model=LeagueResponse)
async def get_league(league_id: str, payload: dict = Depends(verify_token)):
    """Get a league"""
    return league_svc.get_league_by_id(league_id)

@router.delete("/leagues/{league_id}")
async def delete_league(league_id: str, payload: dict = Depends(verify_token)):
    """Delete a league by league_id"""
    return league_svc.delete_league_by_id(league_id)

@router.put("/leagues/{league_id}", response_model=LeagueResponse)
async def update_league(league_id: str, league_request: LeagueRequest, payload: dict = Depends(verify_token)):
    """Update a league by league_id"""
    return league_svc.update_league_by_id(league_id, league_request)

