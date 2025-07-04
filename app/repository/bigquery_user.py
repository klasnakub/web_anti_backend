from typing import Optional
from fastapi import HTTPException, status
from google.cloud import bigquery

class bqUser:
    def __init__(self, client: bigquery.Client, project_id: str, dataset_name: str, table_name: str):
        self.client = client
        self.project_id = project_id
        self.dataset = dataset_name
        self.table = table_name
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username from BigQuery"""
        query = f"""
        SELECT user_id, username, email, password_hash, role, is_active, created_at, last_login
        FROM `{self.project_id}.{self.dataset}.{self.table}`
        WHERE username = @username
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", username),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
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

    def update_last_login(self, user_id: str):
        """Update last_login timestamp for user"""
        query = f"""
        UPDATE `{self.project_id}.{self.dataset}.{self.table}`
        SET last_login = CURRENT_TIMESTAMP()
        WHERE user_id = @user_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            ]
        )
        
        try:
            self.client.query(query, job_config=job_config)
        except Exception as e:
            # Log error but don't fail the login process
            print(f"Failed to update last_login for user {user_id}: {str(e)}")

