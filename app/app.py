from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from config import *
from core.bigquery import BigQueryClient
from core.security import verify_token
from model.league import LeagueRequest, LeagueResponse
from model.login import LoginRequest, LoginResponse
from model.match import MatchRequest, MatchResponse
from model.user import User
from model.url_submission import UrlSubmissionRequest, UrlSubmissionResponse
from repository.bigquery_league_repo import LeagueRepository
from repository.bigquery_match_repo import MatchRepository
from repository.bigquery_user_repo import UserRepository
from repository.bigquery_url_submission_repo import UrlSubmissionRepository
from service.league_svc import LeagueSvc
from service.login_svc import LoginSvc
from service.match_svc import MatchSvc
from service.user_svc import UserSvc
from service.url_submission_svc import UrlSubmissionSvc

# Load environment variables
load_dotenv()

app = FastAPI(title="User Login API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือเฉพาะ origin ที่อนุญาต
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
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

# Init match repo
match_repo = MatchRepository(get_bigquery_client(), PROJECT_ID, DATASET_NAME, table_name="matches", league_table_name="leagues")
# Init match service
match_svc = MatchSvc(match_repo)

# Init url submission repo
url_submission_repo = UrlSubmissionRepository(get_bigquery_client(), PROJECT_ID, DATASET_NAME, "url_submission")
# Init url submission service
url_submission_svc = UrlSubmissionSvc(url_submission_repo)

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

@app.get("/leagues/{league_id}", response_model=LeagueResponse)
async def get_league(league_id: str, payload: dict = Depends(verify_token)):
    """Get a league"""
    return league_svc.get_league_by_id(league_id)

@app.delete("/leagues/{league_id}")
async def delete_league(league_id: str, payload: dict = Depends(verify_token)):
    """Delete a league by league_id"""
    return league_svc.delete_league_by_id(league_id)

@app.put("/leagues/{league_id}", response_model=LeagueResponse)
async def update_league(league_id: str, league_request: LeagueRequest, payload: dict = Depends(verify_token)):
    """Update a league by league_id"""
    return league_svc.update_league_by_id(league_id, league_request)

#@app.post("/matches", response_model=MatchResponse)
@app.post("/matches")
async def add_match(match_request: MatchRequest, payload: dict = Depends(verify_token)):
    """Add a new match"""
    return match_svc.add_match(match_request)

@app.get("/matches", response_model=list[MatchResponse])
async def list_matches(payload: dict = Depends(verify_token)):
    """List all matches"""
    return match_svc.list_all_matches()

@app.get("/matches/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, payload: dict = Depends(verify_token)):
    """Get a match"""
    return match_svc.get_match(match_id)

@app.delete("/matches/{match_id}")
async def delete_match(match_id: int, payload: dict = Depends(verify_token)):
    """Delete a match by match_id"""
    return match_svc.delete_match(match_id)

@app.put("/matches/{match_id}")
async def update_match(match_id: int, match_request: MatchRequest, payload: dict = Depends(verify_token)):
    """Update a match by match_id"""
    return match_svc.update_match(match_id, match_request)

# URL Submission endpoints
@app.post("/url_submission", response_model=UrlSubmissionResponse)
async def add_url_submission(url_submission_request: UrlSubmissionRequest, payload: dict = Depends(verify_token)):
    """Add a new URL submission"""
    return url_submission_svc.add_url_submission(url_submission_request)

@app.get("/url_submission", response_model=list[UrlSubmissionResponse])
async def list_url_submissions(payload: dict = Depends(verify_token)):
    """List all URL submissions"""
    return url_submission_svc.list_all_url_submissions()

@app.get("/url_submission/{submission_id}", response_model=UrlSubmissionResponse)
async def get_url_submission(submission_id: str, payload: dict = Depends(verify_token)):
    """Get a URL submission by ID"""
    submission = url_submission_svc.get_url_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="URL submission not found")
    return submission

@app.put("/url_submission/{submission_id}", response_model=UrlSubmissionResponse)
async def update_url_submission(submission_id: str, url_submission_request: UrlSubmissionRequest, payload: dict = Depends(verify_token)):
    """Update a URL submission by ID"""
    submission = url_submission_svc.update_url_submission(submission_id, url_submission_request)
    if not submission:
        raise HTTPException(status_code=404, detail="URL submission not found")
    return submission

@app.delete("/url_submission/{submission_id}")
async def delete_url_submission(submission_id: str, payload: dict = Depends(verify_token)):
    """Delete a URL submission by ID"""
    success = url_submission_svc.delete_url_submission(submission_id)
    if not success:
        raise HTTPException(status_code=404, detail="URL submission not found")
    return {"message": "URL submission deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 