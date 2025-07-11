from typing import List, Optional
from fastapi import HTTPException, status
from google.cloud import bigquery
from model.file_upload import FileUploadInternal
from repository.fileinfo_repo_interface import IDbFileInfoRepository

class DbFileInfoRepository(IDbFileInfoRepository):
    def __init__(self, client: bigquery.Client, project_id: str, dataset_name: str, table_name: str):
        self.client = client
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.table_name = table_name

    def save_fileinfo(self, fileinfo: FileUploadInternal) -> bool:
        query = f"""
        INSERT INTO `{self.project_id}.{self.dataset_name}.{self.table_name}` (submission_id, file_name, orig_file_name, file_url, file_size, content_type, uploaded_at, bucket_path)
        VALUES (@submission_id, @file_name, @orig_file_name, @file_url, @file_size, @content_type, @uploaded_at, @bucket_path)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("submission_id", "STRING", fileinfo.submission_id),
                bigquery.ScalarQueryParameter("file_name", "STRING", fileinfo.file_name),
                bigquery.ScalarQueryParameter("orig_file_name", "STRING", fileinfo.orig_file_name),
                bigquery.ScalarQueryParameter("file_url", "STRING", fileinfo.file_url),
                bigquery.ScalarQueryParameter("file_size", "STRING", fileinfo.file_size),
                bigquery.ScalarQueryParameter("content_type", "STRING", fileinfo.content_type),
                bigquery.ScalarQueryParameter("uploaded_at", "TIMESTAMP", fileinfo.uploaded_at),
                bigquery.ScalarQueryParameter("bucket_path", "STRING", fileinfo.bucket_path)
            ]
        )
        job = self.client.query(query, job_config=job_config)
        job.result()
        return job.num_dml_affected_rows is not None and job.num_dml_affected_rows > 0


    def get_fileinfo(self, file_name: str) -> Optional[FileUploadInternal]:
        query = f"""
            SELECT submission_id, file_name, file_url, file_size, content_type, uploaded_at, bucket_path
            FROM `{self.project_id}.{self.dataset_name}.{self.table_name}`
            WHERE file_name = @file_name
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("file_name", "STRING", file_name)
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        if results.total_rows == 0:
            return None
        for row in results:
            return FileUploadInternal(
                submission_id=row["submission_id"],
                file_name=row["file_name"],
                file_url=row["file_url"],
                file_size=row["file_size"],
                content_type=row["content_type"],
                uploaded_at=row["uploaded_at"],
                bucket_path=row["bucket_path"]
            )

    def delete_fileinfo(self, file_name: str) -> bool:
        query = f"""
            DELETE FROM `{self.project_id}.{self.dataset_name}.{self.table_name}`
            WHERE file_name = @file_name
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("file_name", "STRING", file_name)
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        query_job.result()
        deleted = query_job.num_dml_affected_rows
        return deleted is not None and deleted > 0

    def get_fileinfo_by_submission_id(self, submission_id: str) -> Optional[List[FileUploadInternal]]:
        query = f"""
            SELECT submission_id, file_name, file_url, file_size, content_type, uploaded_at, bucket_path
            FROM `{self.project_id}.{self.dataset_name}.{self.table_name}`
            WHERE submission_id = @submission_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("submission_id", "STRING", submission_id)
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        if results.total_rows == 0:
            return None
        ret = []
        for row in results:
            ret.append(FileUploadInternal(
                submission_id=row["submission_id"],
                file_name=row["file_name"],
                file_url=row["file_url"],
                file_size=row["file_size"],
                content_type=row["content_type"],
                uploaded_at=row["uploaded_at"],
                bucket_path=row["bucket_path"]
            ))
        return ret
