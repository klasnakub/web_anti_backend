from traceback import print_exception
from fastapi import APIRouter, Depends, HTTPException, status
from config import JWT_EXPIRATION_HOURS
from common import login_svc, user_svc
from core.custom_exception import ItemNotFoundException, UnauthorizedException
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
    try:
        ret = login_svc.do_login(login_request.username, login_request.password, JWT_EXPIRATION_HOURS)
        return ret
    except ItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        ) from e
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        ) from e
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}") from e

@router.get("/me", response_model=User)
async def get_current_user(payload: dict = Depends(verify_token)):
    """Get current user information"""
    try:
        return user_svc.get_user_info(payload["username"])
    except ItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from e
    except Exception as e:
        print_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")
