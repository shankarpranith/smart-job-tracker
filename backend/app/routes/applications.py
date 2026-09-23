import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.models.application import Application, ApplicationCreate

router = APIRouter(prefix="/applications", tags=["applications"])

# Temporary in-memory storage.
# NOTE: This resets every time the server restarts. Replaced by DynamoDB in Phase 3.
fake_db: list[Application] = []

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
    fake_db.append(new_application)
    return new_application


@router.get("", response_model=list[Application])
def list_applications() -> list[Application]:
    """Return all job applications (for the current demo user)."""
    return [app for app in fake_db if app.user_id == TEMP_USER_ID]


@router.get("/{application_id}", response_model=Application)
def get_application(application_id: str) -> Application:
    """Return a single job application by its ID."""
    for app in fake_db:
        if app.application_id == application_id and app.user_id == TEMP_USER_ID:
            return app
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Application with id '{application_id}' not found",
    )