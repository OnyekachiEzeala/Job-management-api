from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models
from app.security import require_role
from app.services.job import job_scheduler
from app.database import get_db
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["jobs"],
)

@router.post("/", response_model=JobResponse, status_code=201)
def create_job(
    job_create: JobCreate, 
    current_user: models.Staff = Depends(require_role("admin")),
    db: Session = Depends(get_db)
    ):
    logger.info(f"Admin {current_user.email} is creating a new job with title: {job_create.title}")
    try:
        if not current_user:
           logger.warning("Unauthorized attempt to create job")
           raise HTTPException(status_code=403, detail="Unauthorized")
        new_job = job_scheduler.create_job(db, job_create)
        db.commit()
        logger.info(f"Job '{new_job.title}' created successfully by admin {current_user.email}")
        return new_job
    
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error creating booking: {http_err.detail}")
        raise http_err

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating job '{job_create.title}': {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create job")
    
@router.get("/", response_model=List[JobResponse], status_code=200)
def get_jobs(
    q: Optional[str] = Query(None, description="Search keyword for service title or description"),
    status: Optional[str] = Query(None, description="Filter by job status"),
    start_time: Optional[datetime] = Query(None, description="Filter jobs starting after this time"),
    end_time: Optional[datetime] = Query(None, description="Filter jobs ending before this time"),
    db: Session = Depends(get_db),
    current_user: models.Staff = Depends(require_role("admin", "staff"))):
    try:
        # if admin: fetch all jobs with optional filters
        if current_user.role == "admin":
            logger.info(f"Admin {current_user.email} is fetching jobs with filters - q: {q}, status: {status}, start_time: {start_time}, end_time: {end_time}")
            jobs = job_scheduler.get_job_by_admin(db, q, status, start_time, end_time)
            logger.info(f"Admin {current_user.email} fetched {len(jobs)} jobs")
            
        else:
            #  if staff: fetch only assigned jobs
            logger.info(f"Staff {current_user.email} is fetching their assigned jobs")
            jobs = job_scheduler.get_job_by_staff(db, current_user.id)
            logger.info(f"Staff {current_user.email} fetched {len(jobs)} assigned jobs")
        return jobs
    
    except Exception as e:
        logger.error(f"Error fetching jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch jobs")
    

@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int, 
    job_update: JobUpdate, 
    db: Session = Depends(get_db),
    current_user: models.Staff = Depends(require_role("admin", "staff"))
    ):
    logger.info(f"User {current_user.email} is attempting to update job with ID: {job_id}")
    try:
        job_data = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job_data:
            logger.warning(f"Job with ID {job_id} not found for update")
            raise HTTPException(status_code=404, detail="Job not found")
        
        #  if cureent_user.role == "admin":
        if current_user.role == "admin":
            logger.info(f"Admin {current_user.email} is updating job with ID: {job_id}")
            updated_job = job_scheduler.update_job_by_admin(db, job_data, job_update)
            db.commit()
            logger.info(f"Admin {current_user.email} successfully updated job with ID: {job_id}")
            return updated_job
        
        # if cureent_user.role == "staff":
        if current_user.role == "staff" and job_data.assigned_to != current_user.id:
            logger.warning(f"Staff {current_user.email} unauthorized to update job with ID: {job_id} assigned to another staff")
            raise HTTPException(status_code=403, detail="Unauthorized to update this job")
        updated_job = job_scheduler.update_job_by_staff(db, job_data, job_update)
        db.commit()
        logger.info(f"Staff {current_user.email} successfully updated job with ID: {job_id}")
        return updated_job
    
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error creating booking: {http_err.detail}")
        raise http_err
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating job with ID {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update job")
    

@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int, 
    current_user: models.Staff = Depends(require_role("admin")),
    db: Session = Depends(get_db)
    ):
    logger.info(f"Admin {current_user.email} is attempting to delete job with ID: {job_id}")
    try:
        job_data = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job_data:
            logger.warning(f"Job with ID {job_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_scheduler.delete_job_by_admin(db, job_data)
        db.commit()
        logger.info(f"Admin {current_user.email} successfully deleted job with ID: {job_id}")
        return
    
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error deleting job: {http_err.detail}")
        raise http_err
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting job with ID {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete job")
