import os
import uuid
from typing import Tuple, Optional
from pathlib import Path
from app.core.config import settings


class StorageService:
    def __init__(self):
        self.backend = settings.STORAGE_BACKEND
        self.local_dir = Path(settings.LOCAL_STORAGE_DIR)
        if self.backend == "local":
            self.local_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, file_bytes: bytes, original_filename: str, content_type: Optional[str] = None) -> Tuple[str, int]:
        """Save file to storage and return (storage_key, size_in_bytes)."""
        file_ext = Path(original_filename).suffix
        unique_key = f"{uuid.uuid4()}{file_ext}"

        if self.backend == "local":
            file_path = self.local_dir / unique_key
            with open(file_path, "wb") as f:
                f.write(file_bytes)
            return str(unique_key), len(file_bytes)
        else:
            # S3 / MinIO backend if configured
            try:
                import boto3
                s3_client = boto3.client(
                    "s3",
                    endpoint_url=settings.S3_ENDPOINT_URL or None,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=settings.S3_REGION
                )
                s3_client.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=unique_key,
                    Body=file_bytes,
                    ContentType=content_type or "application/octet-stream"
                )
                return unique_key, len(file_bytes)
            except Exception:
                # Fallback to local
                file_path = self.local_dir / unique_key
                with open(file_path, "wb") as f:
                    f.write(file_bytes)
                return str(unique_key), len(file_bytes)

    def get_file_bytes(self, storage_key: str) -> Optional[bytes]:
        """Retrieve file content from storage."""
        if self.backend == "local":
            file_path = self.local_dir / storage_key
            if file_path.exists():
                with open(file_path, "rb") as f:
                    return f.read()
            return None
        else:
            try:
                import boto3
                s3_client = boto3.client(
                    "s3",
                    endpoint_url=settings.S3_ENDPOINT_URL or None,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=settings.S3_REGION
                )
                resp = s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=storage_key)
                return resp["Body"].read()
            except Exception:
                file_path = self.local_dir / storage_key
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        return f.read()
                return None

    def delete_file(self, storage_key: str) -> bool:
        """Delete file from storage."""
        if self.backend == "local":
            file_path = self.local_dir / storage_key
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        else:
            try:
                import boto3
                s3_client = boto3.client("s3")
                s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=storage_key)
                return True
            except Exception:
                return False


storage_service = StorageService()
