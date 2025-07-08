from fastapi import APIRouter, Depends, HTTPException
from model.url_submission import UrlSubmissionRequest, UrlSubmissionResponse
from common import url_submission_svc
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
    try:
        return url_submission_svc.add_url_submission(url_submission_request)
    except Exception as e:
        if "URL already exists for this match" in str(e):
            raise HTTPException(status_code=409, detail="URL already exists for this match")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to add URL submission: {str(e)}")

@router.get("/url_submission", response_model=list[UrlSubmissionResponse])
async def list_url_submissions(payload: dict = Depends(verify_token)):
    """List all URL submissions"""
    return url_submission_svc.list_all_url_submissions()

@router.get("/url_submission/{submission_id}", response_model=UrlSubmissionResponse)
async def get_url_submission(submission_id: str, payload: dict = Depends(verify_token)):
    """Get a URL submission by ID"""
    submission = url_submission_svc.get_url_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="URL submission not found")
    return submission

@router.put("/url_submission/{submission_id}", response_model=UrlSubmissionResponse)
async def update_url_submission(submission_id: str, url_submission_request: UrlSubmissionRequest, payload: dict = Depends(verify_token)):
    """Update a URL submission by ID"""
    submission = url_submission_svc.update_url_submission(submission_id, url_submission_request)
    if not submission:
        raise HTTPException(status_code=404, detail="URL submission not found")
    return submission

@router.delete("/url_submission/{submission_id}")
async def delete_url_submission(submission_id: str, payload: dict = Depends(verify_token)):
    """Delete a URL submission by ID"""
    success = url_submission_svc.delete_url_submission(submission_id)
    if not success:
        raise HTTPException(status_code=404, detail="URL submission not found")
    return {"message": "URL submission deleted successfully"}

