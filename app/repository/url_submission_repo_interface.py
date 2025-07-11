from abc import ABC, abstractmethod
from typing import List, Optional
from model.url_submission import UrlSubmissionResponse, UrlSubmissionRequest

class IUrlSubmissionRepository(ABC):
    @abstractmethod
    def add_url_submission(self, url_submission_info: UrlSubmissionRequest) -> Optional[str]:
        pass

    @abstractmethod
    def get_url_submission_by_id(self, submission_id: str) -> Optional[UrlSubmissionResponse]:
        pass

    @abstractmethod
    def list_all_url_submissions(self) -> List[dict]:
        pass

    @abstractmethod
    def update_url_submission(self, submission_id: str, url: Optional[str] = None, type: Optional[str] = None,
                             league_id: Optional[str] = None, match_id: Optional[int] = None,
                             status: Optional[str] = None, image_file_name: Optional[str] = None) -> Optional[UrlSubmissionResponse]:
        pass

    @abstractmethod
    def check_url_exists_in_match(self, url: str, match_id: int) -> bool:
        """Check if a URL already exists for a given match_id"""
        pass

    @abstractmethod
    def delete_url_submission(self, submission_id: str) -> bool:
        pass
