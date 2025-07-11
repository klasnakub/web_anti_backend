from traceback import print_exception
from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from core.custom_exception import ItemNotFoundException
from model.file_upload import FileUploadResponse
from common import file_upload_svc
from core.security import verify_token

router = APIRouter(tags=['upload'])

def is_ready():
    if file_upload_svc:
        return True
    else:
        print(__name__, "Error: league_svc is not set. Please check your configuration.")
        return False

# File Upload endpoints
@router.post("/upload/{submission_id}", response_model=FileUploadResponse)
async def upload_file(submission_id: str, file: UploadFile = File(...), payload: dict = Depends(verify_token)):
    """Upload file to Google Cloud Storage"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to GCS
        if file.filename and file.content_type:
            result = file_upload_svc.upload_file(file_content=file_content, file_name=file.filename, content_type=file.content_type, submission_id=submission_id)
            return result
        raise HTTPException(status_code=403, detail=f"Upload failed: no file uploaded")
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}") from e

@router.delete("/upload/{file_name}")
async def delete_file(file_name: str, payload: dict = Depends(verify_token)):
    """Delete file from Google Cloud Storage"""
    try:
        success = file_upload_svc.delete_file(file_name)
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}") from e
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}

@router.get("/upload/{file_name}")
async def get_fileinfo(file_name: str, payload: dict = Depends(verify_token)) -> FileUploadResponse:
    """Get public URL of file"""
    try:
        file_info = file_upload_svc.get_fileinfo(file_name)
        return file_info
    except ItemNotFoundException as e:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}") from e

@router.get("/upload/list/{submission_id}")
async def get_fileinfo_list(submission_id: str, payload: dict = Depends(verify_token))-> Optional[List[FileUploadResponse]]:
    """Get list of files for a submission"""
    try:
        files = file_upload_svc.get_fileinfo_by_submission_id(submission_id)
        return files
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=500, detail=f"{e}") from e