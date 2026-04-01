from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models import JobStatus

class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: JobStatus = JobStatus.pending
    assigned_to: Optional[int] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: Optional[JobStatus] = None
    assigned_to: Optional[int] = None

class JobResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: JobStatus
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True