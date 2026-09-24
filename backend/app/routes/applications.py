import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.models.application import Application, ApplicationCreate, ApplicationUpdate
from app.repositories import application_repository as repo

router = APIRouter(prefix="/applications", tags=["applications"])

# Hardcoded for now — real user_id will come from Cognito auth in Phase 6.
TEMP_USER_ID = "demo-user-1"


@router.post("", response_model=Application, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate) -> Application:
    """Create a new job application record."""
    now = datetime.now(timezone.utc)
    new_application = Application(
        application_id=str(uuid.uuid4()),
        user_id=TEMP_USER_ID,
        created_at=now,
        updated_at=now,
        **payload.model_dump(),
    )
    return repo.create_item(new_application)


@router.get("", response_model=list[Application])
def list_applications() -> list[Application]:
    """Return all job applications for the current demo user."""
    return repo.list_items(TEMP_USER_ID)


@router.get("/{application_id}", response_model=Application)
def get_application(application_id: str) -> Application:
    """Return a single job application by its ID."""
    app = repo.get_item(TEMP_USER_ID, application_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{application_id}' not found",
        )
    return app


@router.put("/{application_id}", response_model=Application)
def update_application(application_id: str, payload: ApplicationUpdate) -> Application:
    """Update fields on an existing application. Only provided fields are changed."""
    update_data = payload.model_dump(exclude_unset=True, mode="json")
    updated = repo.update_item(TEMP_USER_ID, application_id, update_data)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{application_id}' not found",
        )
    return updated


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: str) -> None:
    """Delete an application by its ID."""
    deleted = repo.delete_item(TEMP_USER_ID, application_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id '{application_id}' not found",
        )