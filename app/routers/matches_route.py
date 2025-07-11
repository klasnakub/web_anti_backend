from traceback import print_exception
from fastapi import APIRouter, Depends, HTTPException, status
from model.match import MatchRequest, MatchResponse
from common import league_svc, match_svc
from core.custom_exception import ItemAlreadyExistsException, ItemNotFoundException
from core.security import verify_token
from fastapi import HTTPException

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

    # check league exits
    league_id = match_request.league_id
    try:
        league_info = league_svc.get_league_by_id(league_id)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found")
    except Exception as e:
        print_exception(e)
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add match: {str(e)}") from e

    try:
        return match_svc.add_match(match_request)
    except ItemAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Match already exists")
    except Exception as e:
        print_exception(e)
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add match: {str(e)}") from e

@router.get("/matches", response_model=list[MatchResponse])
async def list_matches(payload: dict = Depends(verify_token)):
    """List all matches"""
    try:
        return match_svc.list_all_matches()
    except Exception as e:
        print_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch matches data: {str(e)}"
        ) from e

@router.get("/matches/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, payload: dict = Depends(verify_token)):
    """Get a match"""
    try:
        return match_svc.get_match(match_id)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    except Exception as e:
        print_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch match data: {str(e)}"
        ) from e

@router.delete("/matches/{match_id}")
async def delete_match(match_id: int, payload: dict = Depends(verify_token)):
    """Delete a match by match_id"""
    try:
        return match_svc.delete_match(match_id)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    except Exception as e:
        print_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete match: {str(e)}"
        ) from e

@router.put("/matches/{match_id}")
async def update_match(match_id: int, match_request: MatchRequest, payload: dict = Depends(verify_token)):
    """Update a match by match_id"""
    # check league exits
    league_id = match_request.league_id
    try:
        league_info = league_svc.get_league_by_id(league_id)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="League not found")
    except Exception as e:
        print_exception(e)
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add match: {str(e)}") from e

    try:
        return match_svc.update_match(match_id, match_request)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    except Exception as e:
        print_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update match: {str(e)}"
        ) from e
