from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import json
from dotenv import load_dotenv
import uuid

from core.config import *
from core.bigquery import BigQueryClient
from core.security import verify_token
from model.login import LoginRequest, LoginResponse
from model.user import User
from model.league import LeagueRequest, LeagueResponse
from repository.bigquery_user_repo import UserRepository
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

# Database functions
def add_league_to_database(client: bigquery.Client, league_data: dict) -> dict:
    """Add league to BigQuery leagues table"""
    # Generate unique league_id
    league_id = str(uuid.uuid4())
    current_timestamp = datetime.now(timezone.utc)
    
    query = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_NAME}.leagues`
    (league_id, league_name, country, season, status, created_at, updated_at)
    VALUES (@league_id, @league_name, @country, @season, @status, @created_at, @updated_at)
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
            bigquery.ScalarQueryParameter("league_name", "STRING", league_data["league_name"]),
            bigquery.ScalarQueryParameter("country", "STRING", league_data["country"]),
            bigquery.ScalarQueryParameter("season", "STRING", league_data["season"]),
            bigquery.ScalarQueryParameter("status", "STRING", league_data["status"]),
            bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", current_timestamp),
            bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", current_timestamp),
        ]
    )
    
    try:
        client.query(query, job_config=job_config)
        
        return {
            "league_id": league_id,
            "league_name": league_data["league_name"],
            "country": league_data["country"],
            "season": league_data["season"],
            "status": league_data["status"],
            "created_at": current_timestamp,
            "updated_at": current_timestamp
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add league to database: {str(e)}"
        )

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
    client = get_bigquery_client()
    
    # Convert Pydantic model to dict
    league_data = {
        "league_name": league_request.league_name,
        "country": league_request.country,
        "season": league_request.season,
        "status": league_request.status
    }
    
    # Add league to database
    result = add_league_to_database(client, league_data)
    
    return LeagueResponse(**result)

@app.get("/leagues", response_model=list[LeagueResponse])
async def list_leagues(payload: dict = Depends(verify_token)):
    """List all leagues"""
    client = get_bigquery_client()
    query = f"""
        SELECT league_id, league_name, country, season, status, created_at, updated_at
        FROM `{PROJECT_ID}.{DATASET_NAME}.leagues`
        ORDER BY created_at DESC
    """
    try:
        query_job = client.query(query)
        leagues = []
        for row in query_job:
            leagues.append(LeagueResponse(
                league_id=row.league_id,
                league_name=row.league_name,
                country=row.country,
                season=row.season,
                status=row.status,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))
        return leagues
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch leagues: {str(e)}"
        )

@app.delete("/leagues/{league_id}")
async def delete_league(league_id: str, payload: dict = Depends(verify_token)):
    """Delete a league by league_id"""
    client = get_bigquery_client()
    
    # First check if league exists
    check_query = f"""
        SELECT league_id, league_name
        FROM `{PROJECT_ID}.{DATASET_NAME}.leagues`
        WHERE league_id = @league_id
        LIMIT 1
    """
    
    check_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
        ]
    )
    
    try:
        check_job = client.query(check_query, job_config=check_job_config)
        results = list(check_job.result())
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"League with ID {league_id} not found"
            )
        
        # Delete the league
        delete_query = f"""
            DELETE FROM `{PROJECT_ID}.{DATASET_NAME}.leagues`
            WHERE league_id = @league_id
        """
        
        delete_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
            ]
        )
        
        client.query(delete_query, job_config=delete_job_config)
        
        return {
            "message": f"League '{results[0].league_name}' (ID: {league_id}) deleted successfully",
            "league_id": league_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete league: {str(e)}"
        )

@app.put("/leagues/{league_id}", response_model=LeagueResponse)
async def update_league(league_id: str, league_request: LeagueRequest, payload: dict = Depends(verify_token)):
    """Update a league by league_id"""
    client = get_bigquery_client()
    
    # First check if league exists
    check_query = f"""
        SELECT league_id, league_name
        FROM `{PROJECT_ID}.{DATASET_NAME}.leagues`
        WHERE league_id = @league_id
        LIMIT 1
    """
    
    check_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
        ]
    )
    
    try:
        check_job = client.query(check_query, job_config=check_job_config)
        results = list(check_job.result())
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"League with ID {league_id} not found"
            )
        
        # Update the league
        current_timestamp = datetime.utcnow()
        update_query = f"""
            UPDATE `{PROJECT_ID}.{DATASET_NAME}.leagues`
            SET league_name = @league_name,
                country = @country,
                season = @season,
                status = @status,
                updated_at = @updated_at
            WHERE league_id = @league_id
        """
        
        update_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
                bigquery.ScalarQueryParameter("league_name", "STRING", league_request.league_name),
                bigquery.ScalarQueryParameter("country", "STRING", league_request.country),
                bigquery.ScalarQueryParameter("season", "STRING", league_request.season),
                bigquery.ScalarQueryParameter("status", "STRING", league_request.status),
                bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", current_timestamp),
            ]
        )
        
        client.query(update_query, job_config=update_job_config)
        
        # Get the updated league data
        get_updated_query = f"""
            SELECT league_id, league_name, country, season, status, created_at, updated_at
            FROM `{PROJECT_ID}.{DATASET_NAME}.leagues`
            WHERE league_id = @league_id
            LIMIT 1
        """
        
        get_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
            ]
        )
        
        get_job = client.query(get_updated_query, job_config=get_job_config)
        updated_result = list(get_job.result())[0]
        
        return LeagueResponse(
            league_id=updated_result.league_id,
            league_name=updated_result.league_name,
            country=updated_result.country,
            season=updated_result.season,
            status=updated_result.status,
            created_at=updated_result.created_at,
            updated_at=updated_result.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update league: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 