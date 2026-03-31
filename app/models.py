from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    staff = "staff"

class JobStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default=RoleEnum.staff.value)
    created_at = Column(
        DateTime(timezone = True), nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )

    jobs = relationship("Job", back_populates="staff")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    start_time = Column(DateTime(timezone = True), nullable=False)
    end_time = Column(DateTime(timezone = True), nullable=False)
    status = Column(String, default=JobStatus.pending.value)
    assigned_to = Column(Integer, ForeignKey("staff.id"), nullable=True)
    created_at = Column(
        DateTime(timezone = True), nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone = True), nullable=False, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    staff = relationship("Staff", back_populates="jobs")