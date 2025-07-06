from abc import ABC, abstractmethod
from typing import List, Optional

class IUrlSubmissionRepository(ABC):
    @abstractmethod
    def add_url_submission(self, url: str, type: Optional[str] = None, league_id: Optional[str] = None, 
                          match_id: Optional[str] = None, status: Optional[str] = None, 
                          image_file_name: Optional[str] = None) -> dict:
        pass

    @abstractmethod
    def get_url_submission_by_id(self, submission_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def list_all_url_submissions(self) -> List[dict]:
        pass

    @abstractmethod
    def update_url_submission(self, submission_id: str, url: Optional[str] = None, type: Optional[str] = None,
                             league_id: Optional[str] = None, match_id: Optional[str] = None,
                             status: Optional[str] = None, image_file_name: Optional[str] = None) -> Optional[dict]:
        pass

    @abstractmethod
    def delete_url_submission(self, submission_id: str) -> bool:
        pass
