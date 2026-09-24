from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Job
from app.schemas import JobCreate, JobResponse

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.get("", response_model=List[JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    """Fetch all available job openings."""
    return db.query(Job).all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job_by_id(job_id: str, db: Session = Depends(get_db)):
    """Fetch job details by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("", response_model=JobResponse)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """Create or update a job description."""
    existing_job = db.query(Job).filter(Job.id == job_in.id).first()
    if existing_job:
        existing_job.title = job_in.title
        existing_job.description = job_in.description
        existing_job.required_skills = job_in.required_skills
        existing_job.minimum_experience = job_in.minimum_experience
        existing_job.minimum_resume_score = job_in.minimum_resume_score
        existing_job.test_passing_score = job_in.test_passing_score
        db.commit()
        db.refresh(existing_job)
        return existing_job
    
    new_job = Job(**job_in.model_dump())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job
