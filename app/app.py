from dotenv import load_dotenv
# Load environment variables
load_dotenv()

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime, timedelta, timezone

from routers import user_route, leagues_route, matches_route, url_submission_route, file_upload_route

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

services_initialized = True
#import route
for r in user_route, leagues_route, matches_route, url_submission_route, file_upload_route:
    if r.is_ready:
        app.include_router(r.router)
        print("Add router: ", str(r.router.tags))
    else:
        services_initialized = False

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if services_initialized:
        health_status = "healthy"
    else:
        health_status = "error"
    return {"status": health_status, "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 
