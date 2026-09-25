import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.application import Application, ApplicationCreate, ApplicationUpdate
from app.repositories import application_repository as repo
from app.utils.auth import get_current_user_id

from pydantic import BaseModel

from app.services import s3_service

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=Application, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    user_id: str = Depends(get_current_user_id),
) -> Application:
    """Create a new job application record for the authenticated user."""
    now = datetime.now(timezone.utc)
    new_application = Application(
        application_id=str(uuid.uuid4()),
        user_id=user_id,
        created_at=now,
        updated_at=now,
        **payload.model_dump(),
    )
    return repo.create_item(new_application)


@router.get("", response_model=list[Application])
def list_applications(user_id: str = Depends(get_current_user_id)) -> list[Application]:
    """Return all job applications for the authenticated user."""
    return repo.list_items(user_id)


@router.get("/{application_id}", response_model=Application)
def get_application(
    application_id: str,
    user_id: str = Depends(get_current_user_id),
) -> Application:
    """Return a single job application by its ID, if it belongs to the authenticated user."""
    app = repo.get_item(user_id, application_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{application_id}' not found",
        )
    return app


@router.put("/{application_id}", response_model=Application)
def update_application(
    application_id: str,
    payload: ApplicationUpdate,
    user_id: str = Depends(get_current_user_id),
) -> Application:
    """Update fields on an existing application belonging to the authenticated user."""
    update_data = payload.model_dump(exclude_unset=True, mode="json")
    updated = repo.update_item(user_id, application_id, update_data)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{application_id}' not found",
        )
    return updated


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: str,
    user_id: str = Depends(get_current_user_id),
) -> None:
    """Delete an application belonging to the authenticated user."""
    deleted = repo.delete_item(user_id, application_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{application_id}' not found",
        )
        
class ResumeUploadRequest(BaseModel):
    content_type: str


class ResumeUploadResponse(BaseModel):
    upload_url: str
    s3_key: str


@router.post("/{application_id}/resume-upload-url", response_model=ResumeUploadResponse)
def get_resume_upload_url(
    application_id: str,
    payload: ResumeUploadRequest,
    user_id: str = Depends(get_current_user_id),
) -> ResumeUploadResponse:
    """Generate a presigned S3 URL for uploading a resume to this application."""
    app = repo.get_item(user_id, application_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{application_id}' not found",
        )

    try:
        result = s3_service.generate_upload_url(user_id, application_id, payload.content_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Immediately save the s3_key on the application, so we know where
    # the file WILL be even before the client finishes uploading it.
    repo.update_item(user_id, application_id, {"resume_s3_key": result["s3_key"]})

    return ResumeUploadResponse(**result)


@router.get("/{application_id}/resume-download-url")
def get_resume_download_url(
    application_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict:
    """Generate a presigned S3 URL for downloading this application's resume."""
    app = repo.get_item(user_id, application_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{application_id}' not found",
        )
    if app.resume_s3_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume has been uploaded for this application",
        )

    download_url = s3_service.generate_download_url(app.resume_s3_key)
    return {"download_url": download_url}