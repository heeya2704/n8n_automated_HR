from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.models import Candidate, Job, WorkflowLog, ApplicationStatus
from app.services import generate_offer_letter_pdf

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

@router.post("/test-result")
def process_test_result_webhook(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """
    Webhook endpoint to receive test results from n8n or candidate test systems.
    Evaluates score >= 80% passing threshold and updates candidate status.
    """
    candidate_email = payload.get("candidate_email")
    candidate_id = payload.get("candidate_id")
    test_score = payload.get("test_score", 0)

    if not candidate_email and not candidate_id:
        raise HTTPException(status_code=400, detail="candidate_email or candidate_id is required.")

    query = db.query(Candidate)
    if candidate_id:
        candidate = query.filter((Candidate.id == candidate_id) | (Candidate.candidate_id == candidate_id)).first()
    else:
        candidate = query.filter(Candidate.email == candidate_email).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    job = db.query(Job).filter(Job.id == candidate.job_id).first()
    passing_score = job.test_passing_score if job else 80

    is_selected = test_score >= passing_score

    if is_selected:
        candidate.application_status = ApplicationStatus.SELECTED
        candidate.test_score = test_score
        
        pdf_path = generate_offer_letter_pdf(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            job_title=job.title if job else "Python / Machine Learning Developer"
        )
        
        candidate.application_status = ApplicationStatus.OFFER_SENT
        db.commit()

        log = WorkflowLog(
            candidate_id=candidate.id,
            candidate_email=candidate.email,
            workflow_name="n8n Webhook Result",
            status="SELECTED",
            message=f"Scored {test_score}%. Offer letter PDF generated at {pdf_path}",
            test_score=test_score,
            application_status=ApplicationStatus.OFFER_SENT.value
        )
        db.add(log)
        db.commit()

        return {
            "status": "SELECTED",
            "action": "SEND_OFFER",
            "candidate_email": candidate.email,
            "candidate_name": candidate.name,
            "offer_letter_path": pdf_path
        }
    else:
        candidate.application_status = ApplicationStatus.TEST_FAILED
        candidate.test_score = test_score
        db.commit()

        log = WorkflowLog(
            candidate_id=candidate.id,
            candidate_email=candidate.email,
            workflow_name="n8n Webhook Result",
            status="REJECTED",
            message=f"Scored {test_score}%. Below passing threshold {passing_score}%.",
            test_score=test_score,
            application_status=ApplicationStatus.TEST_FAILED.value
        )
        db.add(log)
        db.commit()

        return {
            "status": "REJECTED",
            "action": "SEND_REJECTION",
            "candidate_email": candidate.email,
            "candidate_name": candidate.name
        }
