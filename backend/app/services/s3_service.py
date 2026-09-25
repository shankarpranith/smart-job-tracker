import uuid

import boto3

from app.config import AWS_REGION, S3_RESUME_BUCKET_NAME

_s3_client = boto3.client("s3", region_name=AWS_REGION)

# Presigned URLs expire quickly — long enough for a real upload/download,
# short enough that a leaked URL isn't useful for long.
UPLOAD_URL_EXPIRY_SECONDS = 300  # 5 minutes
DOWNLOAD_URL_EXPIRY_SECONDS = 300  # 5 minutes

ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


def build_resume_key(user_id: str, application_id: str, extension: str) -> str:
    """Build the S3 object key for a resume, namespaced by user and application."""
    unique_suffix = uuid.uuid4().hex[:8]
    return f"resumes/{user_id}/{application_id}/resume-{unique_suffix}.{extension}"


def generate_upload_url(user_id: str, application_id: str, content_type: str) -> dict:
    """Generate a presigned URL the client can PUT a resume file to directly."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(
            f"Unsupported content type '{content_type}'. "
            f"Allowed: {', '.join(ALLOWED_CONTENT_TYPES.keys())}"
        )

    extension = ALLOWED_CONTENT_TYPES[content_type]
    s3_key = build_resume_key(user_id, application_id, extension)

    upload_url = _s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": S3_RESUME_BUCKET_NAME,
            "Key": s3_key,
            "ContentType": content_type,
        },
        ExpiresIn=UPLOAD_URL_EXPIRY_SECONDS,
    )

    return {"upload_url": upload_url, "s3_key": s3_key}


def generate_download_url(s3_key: str) -> str:
    """Generate a presigned URL the client can GET to download/view a resume."""
    return _s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": S3_RESUME_BUCKET_NAME, "Key": s3_key},
        ExpiresIn=DOWNLOAD_URL_EXPIRY_SECONDS,
    )


def delete_resume(s3_key: str) -> None:
    """Delete a resume file from S3 (used when an application is deleted)."""
    _s3_client.delete_object(Bucket=S3_RESUME_BUCKET_NAME, Key=s3_key)