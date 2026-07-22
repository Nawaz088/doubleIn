import uuid
from typing import Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name=settings.S3_REGION,
)


def upload_file(file_bytes: bytes, file_name: str, content_type: str = "application/octet-stream") -> str:
    key = f"{uuid.uuid4().hex}_{file_name}"
    try:
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
        return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET_NAME}/{key}"
    except ClientError as e:
        raise RuntimeError(f"Failed to upload file: {e}")


def delete_file(file_url: str) -> bool:
    try:
        key = file_url.split("/")[-1]
        s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
        return True
    except ClientError:
        return False


def get_presigned_upload_url(file_name: str, content_type: str = "application/octet-stream", expires_in: int = 3600) -> dict:
    key = f"{uuid.uuid4().hex}_{file_name}"
    try:
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.S3_BUCKET_NAME,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )
        return {"upload_url": url, "file_key": key, "file_url": f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET_NAME}/{key}"}
    except ClientError as e:
        raise RuntimeError(f"Failed to generate presigned URL: {e}")


def get_presigned_download_url(file_key: str, expires_in: int = 3600) -> str:
    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": file_key},
            ExpiresIn=expires_in,
        )
    except ClientError:
        return ""
