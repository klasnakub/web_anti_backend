from os import getenv as os_getenv, path as os_path

from fastapi import HTTPException, status
from google.cloud import bigquery
from google.oauth2 import service_account

class BigQueryClient:
    def __init__(self, service_account_file, project_id) -> None:
        self.SERVICE_ACCOUNT_PATH = service_account_file
        self.PROJECT_ID = project_id
        self.client = self.create_bigquery_client()

    def get_bigquery_client(self):
        return self.client

    # BigQuery client initialization
    def create_bigquery_client(self):
        """Initialize BigQuery client with service account credentials"""
        try:
            # Try to use service account file if available
            if os_path.exists(self.SERVICE_ACCOUNT_PATH):
                credentials = service_account.Credentials.from_service_account_file(
                    self.SERVICE_ACCOUNT_PATH,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                return bigquery.Client(credentials=credentials, project=self.PROJECT_ID)
            else:
                # Use default credentials (for Cloud Run)
                return bigquery.Client(project=self.PROJECT_ID)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize BigQuery client: {str(e)}"
            )
