import os
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from dotenv import set_key

from app.database import get_db
from app.models import Candidate, Job, WorkflowLog, ApplicationStatus
from app.services.gmail_service import fetch_candidate_resumes_from_gmail, send_email_via_gmail
from app.services.gemini_service import evaluate_resume_with_gemini, GeminiError
from app.services.notifications import company_name
from app.routes.candidates import process_screening_result
from app.schemas import CandidateScreeningUpdate

router = APIRouter(prefix="/api/gmail", tags=["Gmail Sync"])

@router.post("/configure")
def configure_gmail_credentials(
    gmail_user: str = Body(..., embed=True, description="Gmail address (e.g. hr@company.com)"),
    gmail_app_password: str = Body(..., embed=True, description="16-character Gmail App Password")
):
    """
    Updates the Gmail address and App Password dynamically in .env and runtime environment.
    """
    os.environ["GMAIL_USER"] = gmail_user
    os.environ["GMAIL_APP_PASSWORD"] = gmail_app_password

    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        try:
            set_key(env_path, "GMAIL_USER", gmail_user)
            set_key(env_path, "GMAIL_APP_PASSWORD", gmail_app_password)
        except Exception as e:
            print(f"Could not write to .env: {e}")

    return {
        "status": "SUCCESS",
        "message": f"Gmail credentials updated for {gmail_user}",
        "gmail_user": gmail_user
    }

@router.post("/sync-inbox")
def sync_gmail_inbox_and_process(
    job_id: str = Query("python-ml-developer-001", description="Job ID to match resumes against"),
    db: Session = Depends(get_db)
):
    """
    Connects to HR Gmail inbox via IMAP, fetches candidate resumes,
    evaluates each candidate with Gemini AI, stores candidate records,
    and dispatches candidate Test Link / Rejection emails via Gmail SMTP.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=400, detail="Job ID not found")

    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_password or gmail_password == "your_gmail_app_password":
        return {
            "status": "WARNING",
            "message": "Gmail credentials not configured. Please configure GMAIL_USER and GMAIL_APP_PASSWORD in backend/.env or via /api/gmail/configure.",
            "processed_candidates": []
        }

    # Fetch candidate emails with resume attachments
    resumes = fetch_candidate_resumes_from_gmail(
        gmail_user=gmail_user,
        gmail_password=gmail_password,
        max_emails=10
    )

    processed_list = []

    for item in resumes:
        c_name = item["candidate_name"]
        c_email = item["candidate_email"]
        r_text = item["resume_text"]
        r_file = item["resume_filename"]

        try:
            eval_result = evaluate_resume_with_gemini(resume_text=r_text, job=job)
        except GeminiError as e:
            processed_list.append({"candidate_name": c_name, "candidate_email": c_email, "score": None,
                                   "status": "ERROR", "error": str(e)})
            continue

        score = int(eval_result.get("match_score", 0))
        screening_data = CandidateScreeningUpdate(
            email=c_email,
            name=c_name,
            job_id=job_id,
            resume_score=score,
            resume_analysis=eval_result,
            resume_text=r_text,
            resume_filename=r_file
        )

        result = process_screening_result(screening_data, db=db)
        company = company_name()

        if result["status"] == "DUPLICATE":
            processed_list.append({"candidate_name": c_name, "candidate_email": c_email, "score": score,
                                   "status": "DUPLICATE", "email_sent": False})
            continue

        if result["status"] == "SHORTLISTED":
            subject = f"Online Assessment Test Link - {job.title}"
            email_body = f"""Dear {c_name},

Thank you for applying for the {job.title} position at {company}.

We are pleased to inform you that your resume matched our requirements with a match score of {score}%.

Please complete your online assessment using your unique test link below:

{result['test_link']}

Note:
- Time limit: 30 minutes
- Passing score: {job.test_passing_score}%
- The link expires in 48 hours.

Best regards,
HR Team
{company}"""
        else:
            subject = f"Application Update - {job.title}"
            email_body = f"""Dear {c_name},

Thank you for applying for the {job.title} position at {company}.

After reviewing your application against our job requirements, we are unable to proceed with your application at this stage.

We appreciate your interest in our organization and wish you success in your future endeavors.

Regards,
HR Team
{company}"""

        sent = send_email_via_gmail(
            to_email=c_email,
            subject=subject,
            body=email_body,
            gmail_user=gmail_user,
            gmail_password=gmail_password
        )
        if not sent:
            candidate = db.query(Candidate).filter(Candidate.email == c_email, Candidate.job_id == job_id).first()
            db.add(WorkflowLog(
                candidate_id=candidate.id if candidate else None,
                candidate_email=c_email,
                workflow_name="Resume Screening Email",
                status="EMAIL_FAILED",
                message=f"{subject} email NOT delivered.",
                resume_score=score,
                application_status=candidate.application_status.value if candidate else None,
                error_message="Gmail SMTP send failed"
            ))
            db.commit()

        processed_list.append({
            "candidate_name": c_name,
            "candidate_email": c_email,
            "score": score,
            "status": result["status"],
            "email_sent": sent
        })

    return {
        "status": "SUCCESS",
        "processed_count": len(processed_list),
        "processed_candidates": processed_list
    }
