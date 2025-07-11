from core.custom_exception import ItemNotFoundException
from model.user import User
from repository.user_repo_interface import IUserRepository

class UserSvc:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def get_user_info(self, username: str):
        """Get current user information"""
        user = self.user_repo.get_user_by_username(username)
        
        if not user:
            raise ItemNotFoundException("User not found")
        
        return User(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            last_login=user["last_login"]
        )

