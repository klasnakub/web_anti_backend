from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from fastapi import HTTPException, status
from google.cloud import bigquery
from model.league import LeagueRequest, LeagueResponse
from repository.league_repo_interface import ILeagueRepository

class LeagueRepository(ILeagueRepository):
    def __init__(self, client: bigquery.Client, project_id: str, dataset_name: str, table_name: str):
        self.client = client
        self.project_id = project_id
        self.dataset = dataset_name
        self.table = table_name
    
    def add(self, league_data: LeagueRequest) -> LeagueResponse:
        # Generate unique league_id
        league_id = str(uuid4())
        current_timestamp = datetime.now(timezone.utc)

        query = f"""
        INSERT INTO `{self.project_id}.{self.dataset}.{self.table}`
        (league_id, league_name, country, season, status, created_at, updated_at)
        VALUES (@league_id, @league_name, @country, @season, @status, @created_at, @updated_at)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
                bigquery.ScalarQueryParameter("league_name", "STRING", league_data.league_name),
                bigquery.ScalarQueryParameter("country", "STRING", league_data.country),
                bigquery.ScalarQueryParameter("season", "STRING", league_data.season),
                bigquery.ScalarQueryParameter("status", "STRING", league_data.status),
                bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", current_timestamp),
                bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", current_timestamp),
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        league_info=LeagueResponse(league_id=league_id, league_name=league_data.league_name, country=league_data.country, season=league_data.season, status=league_data.status, created_at=current_timestamp, updated_at=current_timestamp)
        return league_info

    def list(self) -> List[LeagueResponse]:
        """ List all leagues"""
        query = f"""
            SELECT league_id, league_name, country, season, status, created_at, updated_at
            FROM `{self.project_id}.{self.dataset}.{self.table}`
            ORDER BY created_at DESC
        """
        query_job = self.client.query(query)
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
    
    def delete(self, league_id: str) -> int:
        """ Delete a league by league_id"""
        query = f"""
            DELETE FROM `{self.project_id}.{self.dataset}.{self.table}`
            WHERE league_id = @league_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        query_job.result() # wait for job done
        return query_job.num_dml_affected_rows if query_job.num_dml_affected_rows is not None else 0
        
    def get(self, league_id: str) -> Optional[LeagueResponse]:
        query = f"""
            SELECT league_id, league_name, country, season, status, created_at, updated_at
            FROM `{self.project_id}.{self.dataset}.{self.table}`
            WHERE league_id = @league_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        for row in query_job:
            return LeagueResponse(
                league_id=row.league_id,
                league_name=row.league_name,
                country=row.country,
                season=row.season,
                status=row.status,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
        return None
    
    def update(self, league_id: str, leage_info: LeagueRequest) -> int:
        """ Update a league by league_id"""
        current_timestamp = datetime.now(timezone.utc)
        query = f"""
            UPDATE `{self.project_id}.{self.dataset}.{self.table}`
            SET league_name = @league_name, country = @country, season = @season, status = @status, updated_at = @updated_at
            WHERE league_id = @league_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("league_name", "STRING", leage_info.league_name),
                bigquery.ScalarQueryParameter("country", "STRING", leage_info.country),
                bigquery.ScalarQueryParameter("season", "STRING", leage_info.season),
                bigquery.ScalarQueryParameter("status", "STRING", leage_info.status),
                bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", current_timestamp),
                bigquery.ScalarQueryParameter("league_id", "STRING", league_id),
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        query_job.result()
        return query_job.num_dml_affected_rows if query_job.num_dml_affected_rows is not None else 0