from json import loads as json_loads
from fastapi import Form
from repository.url_submission_repo_interface import IUrlSubmissionRepository
from model.url_submission import UrlSubmissionRequest
from typing import List, Optional

class UrlSubmissionSvc:
    def __init__(self, url_submission_repo: IUrlSubmissionRepository):
        self.url_submission_repo = url_submission_repo

    def url_submission_request_form_text(self, url_submission_request_txt: str) -> UrlSubmissionRequest:
        """Get URL submission from json form"""
        try:
            url_submission_request = UrlSubmissionRequest(**json_loads(url_submission_request_txt))
        except Exception as e:
            raise Exception("Invalid URL submission request") 
        return url_submission_request

    def add_url_submission(self, url_submission_request: UrlSubmissionRequest) -> dict:
        """Add a new URL submission"""
        # Check file extension
        if url_submission_request.image_file_name:
            if not url_submission_request.image_file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise Exception("Invalid file type. Only .png, .jpg, and .jpeg files are allowed.")
        # Check if URL already exists for this match_id
        if url_submission_request.match_id:
            url_exists = self.url_submission_repo.check_url_exists_in_match(
                url_submission_request.url, 
                url_submission_request.match_id
            )
            if url_exists:
                raise Exception("URL already exists for this match")
        
        return self.url_submission_repo.add_url_submission(
            url=url_submission_request.url,
            type=url_submission_request.type,
            league_id=url_submission_request.league_id,
            match_id=url_submission_request.match_id,
            status=url_submission_request.status,
            image_file_name=url_submission_request.image_file_name
        )

    def get_url_submission(self, submission_id: str) -> Optional[dict]:
        """Get URL submission by ID"""
        return self.url_submission_repo.get_url_submission_by_id(submission_id)

    def list_all_url_submissions(self) -> List[dict]:
        """List all URL submissions"""
        return self.url_submission_repo.list_all_url_submissions()

    def update_url_submission(self, submission_id: str, url_submission_request: UrlSubmissionRequest) -> Optional[dict]:
        """Update URL submission"""
        return self.url_submission_repo.update_url_submission(
            submission_id=submission_id,
            url=url_submission_request.url,
            type=url_submission_request.type,
            league_id=url_submission_request.league_id,
            match_id=url_submission_request.match_id,
            status=url_submission_request.status,
            image_file_name=url_submission_request.image_file_name
        )

    def delete_url_submission(self, submission_id: str) -> bool:
        """Delete URL submission"""
        return self.url_submission_repo.delete_url_submission(submission_id) 