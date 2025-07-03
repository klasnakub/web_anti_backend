from os import getenv as os_getenv

# Configuration
JWT_SECRET = os_getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# BigQuery Configuration
PROJECT_ID = "practise-bi"
DATASET_NAME = "user"
TABLE_NAME = "users"
SERVICE_ACCOUNT_PATH = os_getenv("GOOGLE_APPLICATION_CREDENTIALS", "practise-bi-88d1549575a4.json")

