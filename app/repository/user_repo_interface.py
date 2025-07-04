from abc import ABC, abstractmethod
from typing import Optional
from model.user import User

class IUserRepository(ABC):
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[dict]:
        pass

    @abstractmethod
    def update_last_login(self, user_id: str):
        pass