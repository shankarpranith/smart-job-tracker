from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    """Allowed values for the status of a job application."""
    SAVED = "Saved"
    APPLIED = "Applied"
    ONLINE_ASSESSMENT = "Online Assessment"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"
    WITHDRAWN = "Withdrawn"


class ApplicationCreate(BaseModel):
    """Fields the client sends when creating a new application."""
    company: str = Field(..., min_length=1, max_length=200)
    job_title: str = Field(..., min_length=1, max_length=200)
    job_url: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    applied_date: Optional[date] = None
    follow_up_date: Optional[date] = None
    job_description: Optional[str] = None
    notes: Optional[str] = None


class Application(ApplicationCreate):
    """Full application record, including server-generated fields."""
    application_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
class ApplicationUpdate(BaseModel):
    """Fields the client can send to update an existing application.
    All fields are optional — the client only sends what changed."""
    company: Optional[str] = Field(None, min_length=1, max_length=200)
    job_title: Optional[str] = Field(None, min_length=1, max_length=200)
    job_url: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    applied_date: Optional[date] = None
    follow_up_date: Optional[date] = None
    job_description: Optional[str] = None
    notes: Optional[str] = None