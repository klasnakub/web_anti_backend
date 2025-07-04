from typing import List, Optional
from fastapi import HTTPException, status
from model.match import MatchRequest, MatchResponse
from repository.bigquery_match_repo import MatchRepository

class MatchSvc():
    def __init__(self, match_repo: MatchRepository):
        self.match_repo = match_repo

    def add_match(self, match_data: MatchRequest) -> Optional[dict]:
        # check if match exists
        m = self.match_repo.get(match_data.match_id)
        if m:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Match already exists")
        ret = self.match_repo.add(match_data)
        if ret:
            return {
                "message": f"Match created successfully",
                "match_id": match_data.match_id
            }
        else:
            return {
                "message": f"Match creation failed",
                "match_id": match_data.match_id
            }

    def list_all_matches(self) -> List[MatchResponse]:
        return self.match_repo.list_all()
    
    def get_match(self, match_id: int) -> Optional[MatchResponse]:
        return self.match_repo.get(match_id)

    def delete_match(self, match_id: int) -> Optional[dict]:
        match_info = self.match_repo.get(match_id)
        print(match_info)
        if not match_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
        deleted = self.match_repo.delete(match_id)
        if deleted:
            return {
                "message": f"Match deleted successfully",
                "match_id": match_id
            }
        else:
            return {
                "message": f"Match delete failed",
                "match_id": match_id
            }
        
    def update_match(self, match_id: int, match_info: MatchRequest) -> Optional[dict]:
        match_exist = self.match_repo.get(match_id)
        if not match_exist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
        ret = self.match_repo.update(match_id, match_info)
        if ret:
            return {
                "message": f"Match updated successfully",
                "match_id": match_id
            }
        else:
            return {
                "message": f"Match update failed",
                "match_id": match_id
            }
            