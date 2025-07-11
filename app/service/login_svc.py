from bcrypt import checkpw as bcrypt_checkpw
from datetime import timedelta
from core.custom_exception import ItemNotFoundException, UnauthorizedException
from core.security import create_access_token
from model.login import LoginResponse
from repository.user_repo_interface import IUserRepository

class LoginSvc:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
    
    def do_login(self, username: str, password: str, session_ttl_hours: int):
        # Get user from database
        user = self.user_repo.get_user_by_username(username)
        
        if not user:
            raise ItemNotFoundException("Invalid username or password")
        
        # Check if user is active
        if not user["is_active"]:
            raise UnauthorizedException("Account is deactivated")
        
        # Verify password
        try:
            password_bytes = password.encode('utf-8')
            stored_hash_bytes = user["password_hash"].encode('utf-8')
            
            if not bcrypt_checkpw(password_bytes, stored_hash_bytes):
                raise UnauthorizedException("Invalid username or password")
        except Exception as e:
            raise
        
        # Update last login
        self.user_repo.update_last_login(user["user_id"])
        
        # Generate JWT token
        access_token_expires = timedelta(hours=session_ttl_hours)
        access_token = create_access_token(
            data={"sub": user["user_id"], "username": user["username"], "role": user["role"]},
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            role=user["role"]
        )

