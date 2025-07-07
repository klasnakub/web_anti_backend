from google.cloud import storage
from datetime import datetime, timezone, timedelta
import uuid
import os
from typing import Optional
from repository.file_repo_interface import IGCSFileRepository

class GCSFileRepository(IGCSFileRepository):
    def __init__(self, bucket_name: str = "web_anti", project_id: str = "practise-bi", service_account_path: Optional[str] = None):
        self.bucket_name = bucket_name
        self.project_id = project_id
        
        # Use service account file if provided
        if service_account_path:
            self.client = storage.Client.from_service_account_json(service_account_path, project=project_id)
        else:
            self.client = storage.Client(project=project_id)
            
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, file_content: bytes, file_name: str, content_type: str) -> dict:
        """Upload file to Google Cloud Storage"""
        # Generate unique file name
        file_extension = os.path.splitext(file_name)[1]
        unique_file_name = f"{uuid.uuid4()}{file_extension}"
        
        # Set blob path
        blob_path = f"Snapshot/{unique_file_name}"
        blob = self.bucket.blob(blob_path)
        
        # Set content type
        blob.content_type = content_type
        
        # Upload file
        blob.upload_from_string(file_content, content_type=content_type)
        
        # Get file size
        blob.reload()
        file_size = blob.size
        
        # Try to generate signed URL, fallback to public URL if no private key
        try:
            file_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET"
            )
        except Exception:
            # Fallback: make public and use public URL
            try:
                blob.make_public()
                file_url = blob.public_url
            except Exception:
                # If uniform bucket-level access is enabled, just return the gs:// URL
                file_url = f"gs://{self.bucket_name}/{blob_path}"
        
        return {
            "file_name": unique_file_name,
            "file_url": file_url,
            "file_size": file_size,
            "content_type": content_type,
            "uploaded_at": datetime.now(timezone.utc),
            "bucket_path": blob_path
        }

    def delete_file(self, file_name: str) -> bool:
        """Delete file from Google Cloud Storage"""
        try:
            blob_path = f"Snapshot/{file_name}"
            blob = self.bucket.blob(blob_path)
            blob.delete()
            return True
        except Exception:
            return False

    def get_file_url(self, file_name: str) -> Optional[str]:
        """Get URL of file"""
        try:
            blob_path = f"Snapshot/{file_name}"
            blob = self.bucket.blob(blob_path)
            
            # Try to generate signed URL, fallback to public URL if no private key
            try:
                file_url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(days=7),
                    method="GET"
                )
            except Exception:
                # Fallback: make public and use public URL
                try:
                    blob.make_public()
                    file_url = blob.public_url
                except Exception:
                    # If uniform bucket-level access is enabled, just return the gs:// URL
                    file_url = f"gs://{self.bucket_name}/{blob_path}"
            
            return file_url
        except Exception:
            return None 