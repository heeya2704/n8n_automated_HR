import os
import secrets
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Candidate, Job, WorkflowLog, TestStatus, ApplicationStatus
from app.schemas import CandidateCreate, CandidateScreeningUpdate, CandidateResponse
from app.services.gemini_service import evaluate_resume_with_gemini, GeminiError
from app.services.pdf_generator import generate_offer_letter_pdf

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])

@router.get("", response_model=List[CandidateResponse])
def get_candidates(
    status: Optional[str] = Query(None, description="Filter by application status"),
    db: Session = Depends(get_db)
):
    """Retrieve all candidates with optional status filtering."""
    query = db.query(Candidate)
    if status:
        query = query.filter(Candidate.application_status == status)
    return query.order_by(Candidate.created_at.desc()).all()

@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate_by_id(candidate_id: str, db: Session = Depends(get_db)):
    """Retrieve candidate details by candidate_id or DB id."""
    candidate = None
    if candidate_id.isdigit():
        candidate = db.query(Candidate).filter(Candidate.id == int(candidate_id)).first()
    if not candidate:
        candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.get("/{candidate_id}/resume")
def download_candidate_resume(candidate_id: str, db: Session = Depends(get_db)):
    """
    Download/retrieve candidate resume as text or file.
    Returns resume text content as plain text.
    """
    candidate = None
    if candidate_id.isdigit():
        candidate = db.query(Candidate).filter(Candidate.id == int(candidate_id)).first()
    if not candidate:
        candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if not candidate.resume_text:
        raise HTTPException(status_code=404, detail="Resume not found for this candidate")

    return {
        "candidate_id": candidate.candidate_id,
        "candidate_email": candidate.email,
        "candidate_name": candidate.name,
        "resume_filename": candidate.resume_filename or "resume.txt",
        "resume_text": candidate.resume_text
    }

@router.get("/{candidate_id}/offer-letter")
def download_offer_letter(candidate_id: str, db: Session = Depends(get_db)):
    """Offer letter PDF for a selected candidate (used by n8n as the email attachment and by HR)."""
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.application_status not in (ApplicationStatus.SELECTED, ApplicationStatus.OFFER_SENT):
        raise HTTPException(status_code=400, detail="Offer letter is only available for selected candidates")
    path = generate_offer_letter_pdf(
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        job_title=candidate.job.title,
    )
    return FileResponse(path, media_type="application/pdf", filename=os.path.basename(path))

@router.post("", response_model=CandidateResponse)
def create_or_register_candidate(candidate_in: CandidateCreate, db: Session = Depends(get_db)):
    """
    Registers a new candidate or updates existing application.
    Enforces duplicate checking based on candidate_email + job_id.
    """
    # Verify Job
    job = db.query(Job).filter(Job.id == candidate_in.job_id).first()
    if not job:
        raise HTTPException(status_code=400, detail=f"Job with ID '{candidate_in.job_id}' does not exist.")

    # Duplicate Check
    existing = db.query(Candidate).filter(
        Candidate.email == candidate_in.email,
        Candidate.job_id == candidate_in.job_id
    ).first()

    if existing:
        # Update existing record
        existing.name = candidate_in.name
        existing.resume_filename = candidate_in.resume_filename or existing.resume_filename
        existing.resume_text = candidate_in.resume_text or existing.resume_text
        if candidate_in.resume_score:
            existing.resume_score = candidate_in.resume_score
        if candidate_in.resume_analysis:
            existing.resume_analysis = candidate_in.resume_analysis
        
        db.commit()
        db.refresh(existing)
        return existing

    # Create new candidate
    new_candidate = Candidate(
        candidate_id=str(uuid.uuid4()),
        name=candidate_in.name,
        email=candidate_in.email,
        job_id=candidate_in.job_id,
        resume_filename=candidate_in.resume_filename,
        resume_text=candidate_in.resume_text,
        resume_score=candidate_in.resume_score or 0,
        resume_analysis=candidate_in.resume_analysis,
        application_status=ApplicationStatus.RECEIVED
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    # Log workflow event
    log = WorkflowLog(
        candidate_id=new_candidate.id,
        candidate_email=new_candidate.email,
        workflow_name="Resume Processing",
        status="APPLICATION_RECEIVED",
        message="Candidate registered in system",
        application_status=ApplicationStatus.RECEIVED.value
    )
    db.add(log)
    db.commit()

    return new_candidate

@router.post("/screen")
def process_screening_result(data: CandidateScreeningUpdate, db: Session = Depends(get_db)):
    """
    Called by n8n or screening pipeline after Gemini AI evaluates the resume.
    If eligible (match_score >= threshold), generates secure test token & link.
    If ineligible, marks status as RESUME_REJECTED.
    """
    candidate = db.query(Candidate).filter(
        Candidate.email == data.email,
        Candidate.job_id == data.job_id
    ).first()

    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=400, detail=f"Job with ID '{data.job_id}' does not exist.")

    if candidate and candidate.application_status not in (
        ApplicationStatus.RECEIVED, ApplicationStatus.RESUME_PROCESSING, ApplicationStatus.ERROR
    ):
        return {
            "status": "DUPLICATE",
            "eligible": None,
            "candidate_id": candidate.candidate_id,
            "candidate_email": candidate.email,
            "candidate_name": candidate.name,
            "application_status": candidate.application_status.value,
            "reason": "Candidate already screened for this job; no action taken."
        }

    if not candidate:
        # Create record on the fly
        candidate = Candidate(
            candidate_id=str(uuid.uuid4()),
            name=data.name or data.email.split('@')[0].capitalize(),
            email=data.email,
            job_id=data.job_id,
            resume_score=data.resume_score,
            resume_analysis=data.resume_analysis,
            resume_text=data.resume_text
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    candidate.resume_score = data.resume_score
    if data.resume_analysis:
        candidate.resume_analysis = data.resume_analysis
    if data.resume_text:
        candidate.resume_text = data.resume_text
    if data.resume_filename:
        candidate.resume_filename = data.resume_filename

    if data.resume_score >= job.minimum_resume_score:
        # Eligible -> Shortlisted & generate secure test token
        candidate.application_status = ApplicationStatus.RESUME_SHORTLISTED
        
        if not candidate.test_token:
            candidate.test_token = secrets.token_hex(32) # 64 chars secure random string
            candidate.test_token_expires_at = datetime.utcnow() + timedelta(hours=48)
            candidate.test_status = TestStatus.NOT_STARTED

        db.commit()
        db.refresh(candidate)

        log = WorkflowLog(
            candidate_id=candidate.id,
            candidate_email=candidate.email,
            workflow_name="Resume Screening",
            status="RESUME_SHORTLISTED",
            message=f"Resume score {data.resume_score}% meets threshold {job.minimum_resume_score}%. Test link generated.",
            resume_score=data.resume_score,
            application_status=ApplicationStatus.RESUME_SHORTLISTED.value
        )
        db.add(log)
        db.commit()

        test_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/test/{candidate.test_token}"
        
        return {
            "status": "SHORTLISTED",
            "eligible": True,
            "candidate_id": candidate.candidate_id,
            "candidate_email": candidate.email,
            "candidate_name": candidate.name,
            "resume_score": data.resume_score,
            "threshold": job.minimum_resume_score,
            "job_title": job.title,
            "test_token": candidate.test_token,
            "test_link": test_link
        }
    else:
        # Ineligible -> Rejected
        candidate.application_status = ApplicationStatus.RESUME_REJECTED
        db.commit()
        db.refresh(candidate)

        log = WorkflowLog(
            candidate_id=candidate.id,
            candidate_email=candidate.email,
            workflow_name="Resume Screening",
            status="RESUME_REJECTED",
            message=f"Resume score {data.resume_score}% below threshold {job.minimum_resume_score}%.",
            resume_score=data.resume_score,
            application_status=ApplicationStatus.RESUME_REJECTED.value
        )
        db.add(log)
        db.commit()

        return {
            "status": "REJECTED",
            "eligible": False,
            "candidate_id": candidate.candidate_id,
            "candidate_email": candidate.email,
            "candidate_name": candidate.name,
            "resume_score": data.resume_score,
            "threshold": job.minimum_resume_score,
            "job_title": job.title,
            "reason": "Resume score does not meet job criteria"
        }

@router.post("/screen-resume")
def screen_resume_with_gemini_ai(
    name: str = Query(..., description="Candidate Name"),
    email: str = Query(..., description="Candidate Email"),
    job_id: str = Query("python-ml-developer-001", description="Job ID"),
    resume_text: str = Body(..., description="Full resume text"),
    db: Session = Depends(get_db)
):
    """
    Directly evaluates candidate resume text against job description using Gemini AI.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=400, detail="Job ID not found")

    try:
        eval_result = evaluate_resume_with_gemini(resume_text=resume_text, job=job)
    except GeminiError as e:
        raise HTTPException(status_code=502, detail=str(e))

    score = int(eval_result.get("match_score", 0))
    is_eligible = score >= job.minimum_resume_score

    screening_data = CandidateScreeningUpdate(
        email=email,
        name=name,
        job_id=job_id,
        resume_score=score,
        eligible=is_eligible,
        resume_analysis=eval_result,
        resume_text=resume_text
    )

    return process_screening_result(screening_data, db=db)

