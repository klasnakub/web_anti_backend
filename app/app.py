from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from config import *
from core.bigquery import BigQueryClient
from core.security import verify_token
from model.login import LoginRequest, LoginResponse
from model.user import User
from model.league import LeagueRequest, LeagueResponse
from repository.bigquery_league_repo import LeagueRepository
from repository.bigquery_user_repo import UserRepository
from service.league_svc import LeagueSvc
from service.login_svc import LoginSvc
from service.user_svc import UserSvc

# Load environment variables
load_dotenv()

app = FastAPI(title="User Login API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือเฉพาะ origin ที่อนุญาต
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init bigquery client
bqclient = BigQueryClient(SERVICE_ACCOUNT_PATH, PROJECT_ID)
get_bigquery_client = bqclient.get_bigquery_client

# Init user repo
user_repo = UserRepository(get_bigquery_client(), PROJECT_ID, DATASET_NAME, TABLE_NAME)
# Init login service
login_svc = LoginSvc(user_repo)
# Init user service
user_svc = UserSvc(user_repo)

# Init league repo
league_repo = LeagueRepository(get_bigquery_client(), PROJECT_ID, DATASET_NAME, "leagues")
# Init league service
league_svc = LeagueSvc(league_repo)

# API endpoints
@app.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """User login endpoint"""
    ret = login_svc.do_login(login_request.username, login_request.password, JWT_EXPIRATION_HOURS)
    return ret

@app.get("/me", response_model=User)
async def get_current_user(payload: dict = Depends(verify_token)):
    """Get current user information"""
    ret = user_svc.get_user_info(payload["username"])
    return ret

@app.post("/leagues", response_model=LeagueResponse)
async def add_league(league_request: LeagueRequest, payload: dict = Depends(verify_token)):
    """Add a new league"""
    return league_svc.add_league_to_database(league_request)

@app.get("/leagues", response_model=list[LeagueResponse])
async def list_leagues(payload: dict = Depends(verify_token)):
    """List all leagues"""
    return league_svc.list_all_leagues()

@app.delete("/leagues/{league_id}")
async def delete_league(league_id: str, payload: dict = Depends(verify_token)):
    """Delete a league by league_id"""
    return league_svc.delete_league_by_id(league_id)

@app.put("/leagues/{league_id}", response_model=LeagueResponse)
async def update_league(league_id: str, league_request: LeagueRequest, payload: dict = Depends(verify_token)):
    """Update a league by league_id"""
    return league_svc.update_league_by_id(league_id, league_request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 