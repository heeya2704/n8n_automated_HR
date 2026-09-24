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
    Evaluates score >= threshold and updates candidate status.

    For SELECTED candidates (score >= threshold):
    - Sets status to SELECTED
    - Generates offer letter PDF
    - Returns PDF path for n8n to attach to email
    - Status remains SELECTED until n8n calls /offer-sent to confirm email delivery

    For REJECTED candidates (score < threshold):
    - Sets status to TEST_FAILED
    - No PDF generated
    - n8n sends rejection email
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
    candidate.test_score = test_score

    if is_selected:
        candidate.application_status = ApplicationStatus.SELECTED
        db.commit()

        pdf_path = generate_offer_letter_pdf(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            job_title=job.title if job else "Python / Machine Learning Developer"
        )

        log = WorkflowLog(
            candidate_id=candidate.id,
            candidate_email=candidate.email,
            workflow_name="Test Result Processing",
            status="SELECTED",
            message=f"Test score {test_score}% meets threshold {passing_score}%. Offer letter PDF generated.",
            test_score=test_score,
            application_status=ApplicationStatus.SELECTED.value
        )
        db.add(log)
        db.commit()

        return {
            "status": "SELECTED",
            "action": "SEND_OFFER",
            "candidate_id": candidate.candidate_id,
            "candidate_email": candidate.email,
            "candidate_name": candidate.name,
            "test_score": test_score,
            "passing_score": passing_score,
            "offer_letter_path": pdf_path,
            "message": "Offer letter PDF ready. n8n should send email and call /offer-sent to confirm delivery."
        }
    else:
        candidate.application_status = ApplicationStatus.TEST_FAILED
        db.commit()

        log = WorkflowLog(
            candidate_id=candidate.id,
            candidate_email=candidate.email,
            workflow_name="Test Result Processing",
            status="REJECTED",
            message=f"Test score {test_score}% below threshold {passing_score}%. Sending rejection email.",
            test_score=test_score,
            application_status=ApplicationStatus.TEST_FAILED.value
        )
        db.add(log)
        db.commit()

        return {
            "status": "REJECTED",
            "action": "SEND_REJECTION",
            "candidate_id": candidate.candidate_id,
            "candidate_email": candidate.email,
            "candidate_name": candidate.name,
            "test_score": test_score,
            "passing_score": passing_score
        }

@router.post("/offer-sent")
def confirm_offer_sent(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """
    Endpoint for n8n to confirm that offer email was successfully sent.
    Updates candidate status to OFFER_SENT only after email delivery is confirmed.

    Expected payload:
    {
      "candidate_email": "...",
      "candidate_id": "..." (optional)
    }
    """
    candidate_email = payload.get("candidate_email")
    candidate_id = payload.get("candidate_id")

    if not candidate_email and not candidate_id:
        raise HTTPException(status_code=400, detail="candidate_email or candidate_id is required.")

    query = db.query(Candidate)
    if candidate_id:
        candidate = query.filter((Candidate.id == candidate_id) | (Candidate.candidate_id == candidate_id)).first()
    else:
        candidate = query.filter(Candidate.email == candidate_email).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    if candidate.application_status == ApplicationStatus.OFFER_SENT:
        return {
            "status": "OFFER_SENT",
            "candidate_email": candidate.email,
            "candidate_name": candidate.name,
            "message": "Already confirmed"
        }

    if candidate.application_status != ApplicationStatus.SELECTED:
        raise HTTPException(
            status_code=400,
            detail=f"Candidate status is {candidate.application_status.value}, expected SELECTED."
        )

    candidate.application_status = ApplicationStatus.OFFER_SENT
    db.commit()

    log = WorkflowLog(
        candidate_id=candidate.id,
        candidate_email=candidate.email,
        workflow_name="Offer Email Delivery",
        status="OFFER_SENT",
        message="Offer email successfully sent to candidate.",
        application_status=ApplicationStatus.OFFER_SENT.value
    )
    db.add(log)
    db.commit()

    return {
        "status": "OFFER_SENT",
        "candidate_email": candidate.email,
        "candidate_name": candidate.name,
        "message": "Candidate status updated to OFFER_SENT"
    }
