from typing import List, Optional
from fastapi import HTTPException, status
from model.league import LeagueRequest, LeagueResponse
from repository.bigquery_league_repo import LeagueRepository
class LeagueSvc():
    def __init__(self, league_repo: LeagueRepository):
        self.league_repo = league_repo
    
    def add_league_to_database(self, league_data: LeagueRequest) -> LeagueResponse:
        return self.league_repo.add(league_data)
    
    def list_all_leagues(self) -> List[LeagueResponse]:
        return self.league_repo.list()
    
    def get_league_by_id(self, league_id: str) -> Optional[LeagueResponse]:
        return self.league_repo.get(league_id)

    def delete_league_by_id(self, league_id: str) -> Optional[dict]:
        league_info=self.league_repo.get(league_id)
        if not league_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"League with ID {league_id} not found"
            )
        ret = self.league_repo.delete(league_id)
        if ret:
            return {
                "message": f"League '{league_info.league_name}' (ID: {league_id}) deleted successfully",
                "league_id": league_id
            }
            
    def update_league_by_id(self, league_id: str, league_data: LeagueRequest) -> Optional[LeagueResponse]:
        # First check if league exists
        league_info=self.league_repo.get(league_id)
        if not league_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"League with ID {league_id} not found"
            )
        # Update the league
        ret = self.league_repo.update(league_id, league_data)

        # Get the updated league data
        return self.league_repo.get(league_id)