from typing import List, Optional
from os import path as os_path
from uuid import uuid4 as uuid_uuid4
from repository.file_repo_interface import IGCSFileRepository
from repository.fileinfo_repo_interface import IDbFileInfoRepository
from model.file_upload import FileUploadResponse, FileUploadInternal

class FileUploadSvc:
    bucket_prefix="Snapshot/"

    def __init__(self, gcs_file_repo: IGCSFileRepository, db_fileinfo_repo: IDbFileInfoRepository):
        self.gcs_file_repo = gcs_file_repo
        self.db_fileinfo_repo = db_fileinfo_repo

    def upload_file(self, file_content: bytes, file_name: str, content_type: str, submission_id: str) -> FileUploadResponse:
        """Upload file to Google Cloud Storage"""
        # TODO: verify is file_extension required??
        #file_extension = os_path.splitext(file_name)[1]
        #unique_file_name = f"{uuid_uuid4()}{file_extension}"
        unique_file_name = f"{uuid_uuid4()}"

        try:
            result = self.gcs_file_repo.upload_file(file_content=file_content, unique_file_name=unique_file_name, content_type=content_type, prefix=self.bucket_prefix)
        except:
            raise Exception("Upload failed")

        try:
            # save upload file info to db
            file_info = FileUploadInternal(
                file_name=unique_file_name,
                orig_file_name=file_name,
                file_url=result["file_url"],
                file_size=result["file_size"],
                content_type=content_type,
                uploaded_at=result["uploaded_at"],
                submission_id=submission_id,
                bucket_path=result["bucket_path"])
            self.db_fileinfo_repo.save_fileinfo(file_info)
        except:
            self.gcs_file_repo.delete_file(file_name=unique_file_name, prefix=self.bucket_prefix)
            raise Exception("Save file info failed")

        return FileUploadResponse(**file_info.model_dump())

    def delete_file(self, file_name: str) -> bool:
        """Delete file from Google Cloud Storage"""
        deleted = self.gcs_file_repo.delete_file(file_name=file_name, prefix=self.bucket_prefix)
        if deleted:
            self.db_fileinfo_repo.delete_fileinfo(file_name)
        return deleted

    def get_file_url(self, file_name: str) -> str:
        """Get public URL of file"""

        # get file url from db
        file_info = self.db_fileinfo_repo.get_fileinfo(file_name=file_name)
        if not file_info:
            raise Exception("File not found")
        url = file_info.file_url

        # get file url from gsc
        #url = self.gcs_file_repo.get_file_url(file_name)
        #if url is None:
        #    raise Exception("File not found")

        return url 

    def get_fileinfo(self, file_name: str) -> Optional[FileUploadResponse]:
        file_info = self.db_fileinfo_repo.get_fileinfo(file_name=file_name)
        if file_info is None:
            return None
        return FileUploadResponse(**file_info.model_dump())

    def get_fileinfo_by_submission_id(self, submission_id: str) -> Optional[List[FileUploadResponse]]:
        files = self.db_fileinfo_repo.get_fileinfo_by_submission_id(submission_id)
        ret = []
        if files is None:
            return ret
        for file_info in files:
            ret.append(FileUploadResponse(**file_info.model_dump()))
        return ret