from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import String, or_, cast
from app.schemas.job import JobResponse, JobCreate, JobUpdate
from sqlalchemy.orm import Session
from app import models


class JobService:
    @staticmethod
    def create_job(db: Session, job_create: JobCreate) -> JobResponse:
    #    check for time validity
        if job_create.start_time >= job_create.end_time:
            raise HTTPException(status_code=400, detail="Start time must be before end time")
        if job_create.start_time < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Start time must be in the future")
        
    #  check for overlapping jobs
        overlapping_job = db.query(models.Job).filter(
            models.Job.assigned_to == job_create.assigned_to,
            models.Job.status.in_(['pending', 'in_progress']),
            models.Job.start_time < job_create.end_time,
            models.Job.end_time > job_create.start_time
        ).first()
        if overlapping_job:
            raise HTTPException(status_code=400, detail="Assigned staff is already engaged in another job during this time")
        
        # check if assigned staff exists
        if job_create.assigned_to is not None:
            staff = db.query(models.Staff).filter(models.Staff.id == job_create.assigned_to).first()
            if not staff:
                raise HTTPException(status_code=400, detail="Assigned staff does not exist")
        
        new_job = models.Job(
            title=job_create.title,
            description=job_create.description,
            start_time=job_create.start_time,
            end_time=job_create.end_time,
            status=job_create.status.value,
            assigned_to=job_create.assigned_to
        )

        db.add(new_job)
        db.flush()
        db.refresh(new_job)
        return JobResponse.model_validate(new_job)
    

    @staticmethod
    def get_job_by_admin(db: Session,
                              q: Optional[str] = None,
                              status: Optional[str] = None,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None
        )-> List[JobResponse]:
        query = db.query(models.Job)
        if q:
           search = f"%{q}%"
           query = query.join(models.Staff).filter(
                or_(
                    cast(models.Staff.id, String).ilike(search),
                    models.Staff.email.ilike(search),
                    models.Job.title.ilike(search),
                    models.Job.description.ilike(search)
                )
            )

        if status is not None:
            query = query.filter(models.Job.status == status)
        if start_time is not None:
            query = query.filter(models.Job.start_time >= start_time)
        if end_time is not None:
            query = query.filter(models.Job.end_time <= end_time)

        jobs = query.all()
        return [JobResponse.model_validate(job) for job in jobs]
    
    @staticmethod
    def get_job_by_staff(db: Session, staff_id: int) -> List[JobResponse]:
        jobs = db.query(models.Job).filter(models.Job.assigned_to == staff_id).all()
        return [JobResponse.model_validate(job) for job in jobs]
    
    @staticmethod
    def update_job_by_admin(db: Session, job_data: models.Job, job_update: JobUpdate) -> JobResponse:
        if job_update.title is not None:
            job_data.title = job_update.title
        if job_update.description is not None:
            job_data.description = job_update.description
        if job_update.start_time is not None:
            if job_update.start_time >= job_data.end_time:
                raise HTTPException(status_code=400, detail="Start time must be before end time")
            if job_update.start_time < datetime.now():
                raise HTTPException(status_code=400, detail="Start time must be in the future")
            job_data.start_time = job_update.start_time
        if job_update.end_time is not None:
            if job_update.end_time <= job_data.start_time:
                raise HTTPException(status_code=400, detail="End time must be after start time")
            job_data.end_time = job_update.end_time
        if job_update.status is not None:
            job_data.status = job_update.status.value
        if job_update.assigned_to is not None:
            overlapping_job = db.query(models.Job).filter(
                models.Job.assigned_to == job_update.assigned_to,
                models.Job.status.in_(['pending', 'in_progress']),
                models.Job.start_time < job_data.end_time,
                models.Job.end_time > job_data.start_time,
                models.Job.id != job_data.id
            ).first()
            if overlapping_job:
                raise HTTPException(status_code=400, detail="Assigned staff is already engaged in another job during this time")
            job_data.assigned_to = job_update.assigned_to

        db.add(job_data)
        db.flush()
        db.refresh(job_data)
        return JobResponse.model_validate(job_data)
    
    @staticmethod
    def update_job_by_staff(db: Session, job_data: models.Job, job_update: JobUpdate) -> JobResponse:
        if job_update.status is not None:
            if job_update.status.value not in ['in_progress', 'completed']:
                raise HTTPException(status_code=400, detail="Staff can only update job status to 'in_progress' or 'completed'")
            job_data.status = job_update.status.value
        db.add(job_data)
        db.flush()
        db.refresh(job_data)
        return JobResponse.model_validate(job_data)

    @staticmethod
    def delete_job_by_admin(db: Session, job_data: models.Job):
        db.delete(job_data)
        db.flush()
        return

        










job_scheduler = JobService()