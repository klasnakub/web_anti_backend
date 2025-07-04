from fastapi import HTTPException, status
from model.user import User
from repository.bigquery_user import bqUser

class UserSvc:
    def __init__(self, user_repo: bqUser):
        self.user_repo = user_repo

    def get_user_info(self, username: str):
        """Get current user information"""
        user = self.user_repo.get_user_by_username(username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return User(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            last_login=user["last_login"]
        )

