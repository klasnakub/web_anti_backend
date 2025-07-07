from abc import ABC, abstractmethod
from typing import List, Optional
from model.league import LeagueRequest, LeagueResponse

class ILeagueRepository(ABC):
    @abstractmethod
    def add(self, league_data: LeagueRequest) -> LeagueResponse:
        pass

    @abstractmethod
    def list(self) -> List[LeagueResponse]:
        pass

    @abstractmethod
    def delete(self, league_id: str) -> int:
        pass

    @abstractmethod
    def get(self, league_id: str) -> Optional[LeagueResponse]:
        pass

    @abstractmethod
    def update(self, league_id: str, leage_info: LeagueRequest) -> Optional[LeagueResponse]:
        pass
