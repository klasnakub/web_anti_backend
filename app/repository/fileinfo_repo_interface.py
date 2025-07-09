from abc import ABC, abstractmethod
from typing import List, Optional
from model.file_upload import FileUploadInternal

class IDbFileInfoRepository(ABC):
    @abstractmethod
    def get_fileinfo_by_submission_id(self, submission_id: str) -> Optional[List[FileUploadInternal]]:
        pass

    @abstractmethod
    def get_fileinfo(self, file_name: str) -> Optional[FileUploadInternal]:
        pass

    @abstractmethod
    def save_fileinfo(self, fileinfo: FileUploadInternal) -> bool:
        pass

    @abstractmethod
    def delete_fileinfo(self, file_name: str) -> bool:
        pass