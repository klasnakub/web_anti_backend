from typing import Optional, List
from fastapi import HTTPException, status
from google.cloud import bigquery
from model.match import MatchRequest, MatchResponse
from repository.match_repo_interface import IMatchRepository

"""
CREATE TABLE user.matches (
  match_id NUMERIC,
  home_team STRING,
  away_team STRING,
  league_id STRING REFERENCES user.leagues(league_id) NOT ENFORCED,
  match_date TIMESTAMP,
  status STRING,
  PRIMARY KEY(match_id) NOT ENFORCED
)
"""

class MatchRepository(IMatchRepository):
    def __init__(self, client: bigquery.Client, project_id: str, dataset_name: str, table_name: str, league_table_name: str):
        self.client = client
        self.project_id = project_id
        self.dataset = dataset_name
        self.table = table_name
        self.league_table = league_table_name

    def list_all(self) -> List[MatchResponse]:
        """List all matches"""
        query = f"""
            SELECT m.match_id, m.home_team, m.away_team, m.league_id, m.match_date, m.status, l.league_name 
            FROM {self.dataset}.{self.table} m LEFT JOIN {self.dataset}.{self.league_table} l USING (league_id) 
            ORDER BY m.match_date DESC;"""
        try:
            query_job = self.client.query(query)
            matches = []
            for row in query_job:
                matches.append(MatchResponse(
                    match_id=row.match_id,
                    home_team=row.home_team,
                    away_team=row.away_team,
                    match_date=row.match_date,
                    league_id=row.league_id,
                    league_name=row.league_name,
                    status=row.status
                ))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch leagues: {str(e)}"
            )
        return matches
    
    def add(self, match_data: MatchRequest) -> int:
        """Add match"""
        query = f"""
            INSERT INTO `{self.project_id}.{self.dataset}.{self.table}`
            (match_id, home_team, away_team, league_id, match_date, status)
            VALUES (@match_id, @home_team, @away_team, @league_id, @match_date, @status)
        """        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("match_id", "NUMERIC", match_data.match_id),
                bigquery.ScalarQueryParameter("home_team", "STRING", match_data.home_team),
                bigquery.ScalarQueryParameter("away_team", "STRING", match_data.away_team),
                bigquery.ScalarQueryParameter("league_id", "STRING", match_data.league_id),
                bigquery.ScalarQueryParameter("match_date", "TIMESTAMP", match_data.match_date),
                bigquery.ScalarQueryParameter("status", "STRING", match_data.status),
            ]
        )
        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result() # wait for job done
            inserted = 0
            if query_job.dml_stats:
                #print(query_job.dml_stats)
                inserted = query_job.dml_stats.inserted_row_count
            return inserted
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add match: {str(e)}"
            )

    def get(self, match_id: int) -> Optional[MatchResponse]:
        """Get match info"""
        query = f"""
            SELECT m.match_id, m.home_team, m.away_team, m.league_id, l.league_name, m.match_date, m.status
            FROM `{self.project_id}.{self.dataset}.{self.table}` m LEFT JOIN {self.dataset}.{self.league_table} l USING (league_id) 
            WHERE match_id = @match_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("match_id", "NUMERIC", match_id),
            ]
        )
        try:
            query_job = self.client.query(query, job_config=job_config)
            for row in query_job:
                return MatchResponse(
                    match_id=row.match_id,
                    home_team=row.home_team,
                    away_team=row.away_team,
                    league_id=row.league_id,
                    league_name=row.league_name,
                    match_date=row.match_date,
                    status=row.status
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch match: {str(e)}"
            )
        return None

    def delete(self, match_id: int) -> Optional[int]:
        """Delete a match"""
        query = f"""
            DELETE FROM `{self.project_id}.{self.dataset}.{self.table}`
            WHERE match_id = @match_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("match_id", "NUMERIC", match_id),
            ]
        )
        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result() # wait for job done
            deleted = 0
            if query_job.dml_stats:
                deleted = query_job.dml_stats.deleted_row_count
            return deleted
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete match: {str(e)}"
            )

    def update(self, match_id: int, match_info: MatchRequest) -> int:
        """Update a match"""
        query = f"""
            UPDATE `{self.project_id}.{self.dataset}.{self.table}`
            SET home_team = @home_team, away_team = @away_team, league_id = @league_id, match_date = @match_date, status = @status
            WHERE match_id = @match_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("match_id", "NUMERIC", match_id),
                bigquery.ScalarQueryParameter("home_team", "STRING", match_info.home_team),
                bigquery.ScalarQueryParameter("away_team", "STRING", match_info.away_team),
                bigquery.ScalarQueryParameter("league_id", "STRING", match_info.league_id),
                bigquery.ScalarQueryParameter("match_date", "TIMESTAMP", match_info.match_date),
                bigquery.ScalarQueryParameter("status", "STRING", match_info.status),
            ]
        )
        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            updated = 0
            if query_job.dml_stats:
                updated = query_job.dml_stats.updated_row_count
            return updated
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update match: {str(e)}"
            )