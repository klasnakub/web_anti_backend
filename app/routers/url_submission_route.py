from traceback import print_exception
from fastapi import APIRouter, Depends, HTTPException
from core.custom_exception import ItemAlreadyExistsException, ItemNotFoundException
from model.url_submission import UrlSubmissionRequest, UrlSubmissionResponse
from common import league_svc, match_svc, url_submission_svc
from core.security import verify_token

router = APIRouter(tags=['url_sumbission'])

def is_ready():
    if url_submission_svc:
        return True
    else:
        print(__name__, "Error: url_submission_svc is not set. Please check your configuration.")
        return False

# URL Submission endpoints
@router.post("/url_submission", response_model=UrlSubmissionResponse)
async def add_url_submission(url_submission_request: UrlSubmissionRequest, payload: dict = Depends(verify_token)):
    """Add a new URL submission"""
    # check league and match exists
    check_league_and_match_exists(league_id=url_submission_request.league_id, match_id=url_submission_request.match_id)

    try:
        return url_submission_svc.add_url_submission(url_submission_request)
    except ItemAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail="URL already exists for this match") from e
    except ItemNotFoundException as e:
        raise HTTPException(status_code=404, detail="URL submission not found. Possible add failed.") from e
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to add URL submission: {str(e)}") from e

@router.get("/url_submission", response_model=list[UrlSubmissionResponse])
async def list_url_submissions(payload: dict = Depends(verify_token)):
    """List all URL submissions"""
    try:
        return url_submission_svc.list_all_url_submissions()
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to get URL submission: {str(e)}") from e

@router.get("/url_submission/{submission_id}", response_model=UrlSubmissionResponse)
async def get_url_submission(submission_id: str, payload: dict = Depends(verify_token)):
    """Get a URL submission by ID"""
    try:
        return url_submission_svc.get_url_submission(submission_id)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=404, detail="URL submission not found") from e
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to get URL submission: {str(e)}") from e

@router.put("/url_submission/{submission_id}", response_model=UrlSubmissionResponse)
async def update_url_submission(submission_id: str, url_submission_request: UrlSubmissionRequest, payload: dict = Depends(verify_token)):
    """Update a URL submission by ID"""
    # check league and match exists
    check_league_and_match_exists(league_id=url_submission_request.league_id, match_id=url_submission_request.match_id)

    try:
        return url_submission_svc.update_url_submission(submission_id, url_submission_request)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=404, detail="URL submission not found") from e
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to update URL submission: {str(e)}") from e

@router.delete("/url_submission/{submission_id}")
async def delete_url_submission(submission_id: str, payload: dict = Depends(verify_token)):
    """Delete a URL submission by ID"""
    # TODO: make sure no upload file remain before delete, TBC: automatic delete related upload file?
    try:
        success = url_submission_svc.delete_url_submission(submission_id)
        if not success:
            raise HTTPException(status_code=404, detail="URL submission not found")
        return {"message": "URL submission deleted successfully"}
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to delete URL submission: {str(e)}") from e


def check_league_and_match_exists(league_id: str, match_id: int):
    """
    Checks if a league and a match exist by their respective IDs.

    Args:
        league_id (str): The unique identifier of the league to check.
        match_id (int): The unique identifier of the match to check.

    Raises:
        HTTPException: If the league with the given ID does not exist (404).
        HTTPException: If the match with the given ID does not exist (404).
    """

    # check league exists
    try:
        league_data = league_svc.get_league_by_id(league_id)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=404, detail="League not found")

    # check match exists
    try:
        match_data = match_svc.get_match(match_id)
    except ItemNotFoundException as e:
        raise HTTPException(status_code=404, detail="Match not found")