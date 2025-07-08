from fastapi import APIRouter, Depends
from config import JWT_EXPIRATION_HOURS
from common import login_svc, user_svc
from core.security import verify_token
from model.login import LoginRequest, LoginResponse
from model.user import User

router = APIRouter(tags=['user'])

def is_ready():
    if user_svc:
        return True
    else:
        print(__name__, "Error: league_svc is not set. Please check your configuration.")
        return False

@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """User login endpoint"""
    ret = login_svc.do_login(login_request.username, login_request.password, JWT_EXPIRATION_HOURS)
    return ret

@router.get("/me", response_model=User)
async def get_current_user(payload: dict = Depends(verify_token)):
    """Get current user information"""
    ret = user_svc.get_user_info(payload["username"])
    return ret
