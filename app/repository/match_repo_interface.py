from abc import ABC, abstractmethod
from typing import List, Optional
from model.match import MatchRequest, MatchResponse

class IMatchRepository(ABC):
    @abstractmethod
    def list_all(self) -> List[MatchResponse]:
        pass

    @abstractmethod
    def add(self, match_data: MatchRequest) -> int:
        pass

    @abstractmethod
    def get(self, match_id: int) -> Optional[MatchResponse]:
        pass
    
    @abstractmethod
    def delete(self, match_id: int) -> Optional[int]:
        pass

    @abstractmethod
    def update(self, match_id: int, match_info: MatchRequest) -> int:
        pass
