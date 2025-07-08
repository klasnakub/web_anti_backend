from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
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
@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...), payload: dict = Depends(verify_token)):
    """Upload file to Google Cloud Storage"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to GCS
        result = file_upload_svc.upload_file(file_content, file.filename, file.content_type) # type: ignore
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.delete("/upload/{file_name}")
async def delete_file(file_name: str, payload: dict = Depends(verify_token)):
    """Delete file from Google Cloud Storage"""
    success = file_upload_svc.delete_file(file_name)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}

@router.get("/upload/{file_name}")
async def get_file_url(file_name: str, payload: dict = Depends(verify_token)):
    """Get public URL of file"""
    try:
        url = file_upload_svc.get_file_url(file_name)
        return {"file_name": file_name, "file_url": url}
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")

