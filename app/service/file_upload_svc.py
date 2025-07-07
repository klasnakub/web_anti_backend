from repository.file_repo_interface import IGCSFileRepository
from model.file_upload import FileUploadResponse

class FileUploadSvc:
    def __init__(self, gcs_file_repo: IGCSFileRepository):
        self.gcs_file_repo = gcs_file_repo

    def upload_file(self, file_content: bytes, file_name: str, content_type: str) -> FileUploadResponse:
        """Upload file to Google Cloud Storage"""
        result = self.gcs_file_repo.upload_file(file_content, file_name, content_type)
        return FileUploadResponse(**result)

    def delete_file(self, file_name: str) -> bool:
        """Delete file from Google Cloud Storage"""
        return self.gcs_file_repo.delete_file(file_name)

    def get_file_url(self, file_name: str) -> str:
        """Get public URL of file"""
        url = self.gcs_file_repo.get_file_url(file_name)
        if url is None:
            raise Exception("File not found")
        return url 