from google.cloud import bigquery
from datetime import datetime, timezone
import uuid
from typing import List, Optional

class UrlSubmissionRepository:
    def __init__(self, client: bigquery.Client, project_id: str, dataset_name: str, table_name: str = "url_submission"):
        self.client = client
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.table_name = table_name
        self.table_id = f"{project_id}.{dataset_name}.{table_name}"

    def add_url_submission(self, url: str, type: Optional[str] = None, league_id: Optional[str] = None, 
                          match_id: Optional[str] = None, status: Optional[str] = None, 
                          image_file_name: Optional[str] = None) -> dict:
        """Add a new URL submission to BigQuery"""
        submission_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)
        
        query = f"""
        INSERT INTO `{self.table_id}`
        (submission_id, url, type, league_id, match_id, status, image_file_name, created_at, updated_at)
        VALUES (@submission_id, @url, @type, @league_id, @match_id, @status, @image_file_name, @created_at, @updated_at)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("submission_id", "STRING", submission_id),
                bigquery.ScalarQueryParameter("url", "STRING", url),
                bigquery.ScalarQueryParameter("type", "STRING", type),
                bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
                bigquery.ScalarQueryParameter("match_id", "STRING", match_id),
                bigquery.ScalarQueryParameter("status", "STRING", status),
                bigquery.ScalarQueryParameter("image_file_name", "STRING", image_file_name),
                bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", current_time),
                bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", current_time),
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()  # Wait for the query to complete
            
            return {
                "submission_id": submission_id,
                "url": url,
                "type": type,
                "league_id": league_id,
                "match_id": match_id,
                "status": status,
                "image_file_name": image_file_name,
                "created_at": current_time,
                "updated_at": current_time
            }
        except Exception as e:
            raise Exception(f"Error inserting row: {str(e)}")

    def get_url_submission_by_id(self, submission_id: str) -> Optional[dict]:
        """Get URL submission by submission_id with league and match information"""
        query = f"""
        SELECT 
            us.submission_id,
            us.url,
            us.type,
            us.league_id,
            us.match_id,
            us.status,
            us.image_file_name,
            us.created_at,
            us.updated_at,
            l.league_name,
            CONCAT(m.home_team, ' VS ', m.away_team, ' (', FORMAT_DATETIME('%Y-%m-%d', m.match_date), ')') as matches_name
        FROM `{self.table_id}` us
        LEFT JOIN `{self.project_id}.{self.dataset_name}.leagues` l ON us.league_id = l.league_id
        LEFT JOIN `{self.project_id}.{self.dataset_name}.matches` m ON us.match_id = CAST(m.match_id AS STRING)
        WHERE us.submission_id = @submission_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("submission_id", "STRING", submission_id),
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        results = list(query_job)
        
        if results:
            row = results[0]
            return {
                "submission_id": row.submission_id,
                "url": row.url,
                "type": row.type,
                "league_id": row.league_id,
                "match_id": row.match_id,
                "status": row.status,
                "image_file_name": row.image_file_name,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "league_name": row.league_name,
                "matches_name": row.matches_name
            }
        return None

    def list_all_url_submissions(self) -> List[dict]:
        """List all URL submissions with league and match information"""
        query = f"""
        SELECT 
            us.submission_id,
            us.url,
            us.type,
            us.league_id,
            us.match_id,
            us.status,
            us.image_file_name,
            us.created_at,
            us.updated_at,
            l.league_name,
            CONCAT(m.home_team, ' VS ', m.away_team, ' (', FORMAT_DATETIME('%Y-%m-%d', m.match_date), ')') as matches_name
        FROM `{self.table_id}` us
        LEFT JOIN `{self.project_id}.{self.dataset_name}.leagues` l ON us.league_id = l.league_id
        LEFT JOIN `{self.project_id}.{self.dataset_name}.matches` m ON us.match_id = CAST(m.match_id AS STRING)
        ORDER BY us.created_at DESC
        """
        
        query_job = self.client.query(query)
        results = list(query_job)
        
        submissions = []
        for row in results:
            submissions.append({
                "submission_id": row.submission_id,
                "url": row.url,
                "type": row.type,
                "league_id": row.league_id,
                "match_id": row.match_id,
                "status": row.status,
                "image_file_name": row.image_file_name,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "league_name": row.league_name,
                "matches_name": row.matches_name
            })
        
        return submissions

    def update_url_submission(self, submission_id: str, url: Optional[str] = None, type: Optional[str] = None,
                             league_id: Optional[str] = None, match_id: Optional[str] = None,
                             status: Optional[str] = None, image_file_name: Optional[str] = None) -> Optional[dict]:
        """Update URL submission by submission_id"""
        current_time = datetime.now(timezone.utc)
        
        # Build dynamic update query
        update_fields = []
        query_params = [
            bigquery.ScalarQueryParameter("submission_id", "STRING", submission_id),
            bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", current_time)
        ]
        
        if url is not None:
            update_fields.append("url = @url")
            query_params.append(bigquery.ScalarQueryParameter("url", "STRING", url))
        
        if type is not None:
            update_fields.append("type = @type")
            query_params.append(bigquery.ScalarQueryParameter("type", "STRING", type))
        
        if league_id is not None:
            update_fields.append("league_id = @league_id")
            query_params.append(bigquery.ScalarQueryParameter("league_id", "STRING", league_id))
        
        if match_id is not None:
            update_fields.append("match_id = @match_id")
            query_params.append(bigquery.ScalarQueryParameter("match_id", "STRING", match_id))
        
        if status is not None:
            update_fields.append("status = @status")
            query_params.append(bigquery.ScalarQueryParameter("status", "STRING", status))
        
        if image_file_name is not None:
            update_fields.append("image_file_name = @image_file_name")
            query_params.append(bigquery.ScalarQueryParameter("image_file_name", "STRING", image_file_name))
        
        if not update_fields:
            return self.get_url_submission_by_id(submission_id)
        
        update_fields.append("updated_at = @updated_at")
        
        query = f"""
        UPDATE `{self.table_id}`
        SET {', '.join(update_fields)}
        WHERE submission_id = @submission_id
        """
        
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        query_job = self.client.query(query, job_config=job_config)
        query_job.result()  # Wait for the query to complete
        
        return self.get_url_submission_by_id(submission_id)

    def check_url_exists_in_match(self, url: str, match_id: str) -> bool:
        """Check if URL already exists for a specific match_id"""
        query = f"""
        SELECT COUNT(*) as count
        FROM `{self.table_id}`
        WHERE url = @url AND match_id = @match_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("url", "STRING", url),
                bigquery.ScalarQueryParameter("match_id", "STRING", match_id),
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        results = list(query_job)
        
        return results[0].count > 0

    def delete_url_submission(self, submission_id: str) -> bool:
        """Delete URL submission by submission_id"""
        query = f"""
        DELETE FROM `{self.table_id}`
        WHERE submission_id = @submission_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("submission_id", "STRING", submission_id),
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        query_job.result()  # Wait for the query to complete
        
        # Check if any rows were affected
        return query_job.num_dml_affected_rows > 0 