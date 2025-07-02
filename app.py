from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from google.cloud import bigquery
from google.oauth2 import service_account
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional
import json
from dotenv import load_dotenv
import uuid

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

# Security
security = HTTPBearer()

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# BigQuery Configuration
PROJECT_ID = "practise-bi"
DATASET_NAME = "user"
TABLE_NAME = "users"
SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "practise-bi-88d1549575a4.json")

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str
    email: str
    role: str

class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class LeagueRequest(BaseModel):
    league_name: str
    country: str
    season: str
    status: str

class LeagueResponse(BaseModel):
    league_id: str
    league_name: str
    country: str
    season: str
    status: str
    created_at: datetime
    updated_at: datetime

# BigQuery client initialization
def get_bigquery_client():
    """Initialize BigQuery client with service account credentials"""
    try:
        # Try to use service account file if available
        if os.path.exists(SERVICE_ACCOUNT_PATH):
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_PATH,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            return bigquery.Client(credentials=credentials, project=PROJECT_ID)
        else:
            # Use default credentials (for Cloud Run)
            return bigquery.Client(project=PROJECT_ID)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize BigQuery client: {str(e)}"
        )

# JWT functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Database functions
def get_user_by_username(client: bigquery.Client, username: str) -> Optional[dict]:
    """Get user by username from BigQuery"""
    query = f"""
    SELECT user_id, username, email, password_hash, role, is_active, created_at, last_login
    FROM `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
    WHERE username = @username
    LIMIT 1
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", username),
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        if results:
            row = results[0]
            return {
                "user_id": row.user_id,
                "username": row.username,
                "email": row.email,
                "password_hash": row.password_hash,
                "role": row.role,
                "is_active": row.is_active,
                "created_at": row.created_at,
                "last_login": row.last_login
            }
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {str(e)}"
        )

def update_last_login(client: bigquery.Client, user_id: str):
    """Update last_login timestamp for user"""
    query = f"""
    UPDATE `{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}`
    SET last_login = CURRENT_TIMESTAMP()
    WHERE user_id = @user_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        ]
    )
    
    try:
        client.query(query, job_config=job_config)
    except Exception as e:
        # Log error but don't fail the login process
        print(f"Failed to update last_login for user {user_id}: {str(e)}")

def add_league_to_database(client: bigquery.Client, league_data: dict) -> dict:
    """Add league to BigQuery leagues table"""
    # Generate unique league_id
    league_id = str(uuid.uuid4())
    current_timestamp = datetime.utcnow()
    
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
    client = get_bigquery_client()
    
    # Get user from database
    user = get_user_by_username(client, login_request.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Verify password
    try:
        password_bytes = login_request.password.encode('utf-8')
        stored_hash_bytes = user["password_hash"].encode('utf-8')
        
        if not bcrypt.checkpw(password_bytes, stored_hash_bytes):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Update last login
    update_last_login(client, user["user_id"])
    
    # Generate JWT token
    access_token_expires = timedelta(hours=JWT_EXPIRATION_HOURS)
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

@app.get("/me", response_model=User)
async def get_current_user(payload: dict = Depends(verify_token)):
    """Get current user information"""
    client = get_bigquery_client()
    
    user = get_user_by_username(client, payload["username"])
    
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