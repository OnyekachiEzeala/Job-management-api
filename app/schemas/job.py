from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models import JobStatus

class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: JobStatus = JobStatus.pending
    assigned_to: Optional[int] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    assigned_to: Optional[int] = None

class JobResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: JobStatus
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True