import os
import logging
from sqlalchemy.orm import Session
from app.models import Candidate, Job, WorkflowLog, ApplicationStatus
from app.services.gmail_service import send_email_via_gmail
from app.services.n8n_client import trigger_n8n_test_result_webhook
from app.services.pdf_generator import generate_offer_letter_pdf

logger = logging.getLogger(__name__)


def company_name() -> str:
    return os.getenv("COMPANY_NAME", "TechCorp Solutions")


def build_acceptance_email(candidate: Candidate, job: Job) -> tuple[str, str]:
    company = company_name()
    subject = f"Congratulations! You have been selected - {job.title} at {company}"
    body = f"""Dear {candidate.name},

We are delighted to inform you that you have been selected for the position of {job.title} at {company}.

Selection summary:
- Position: {job.title}
- Resume match score: {candidate.resume_score}%
- Assessment score: {candidate.test_score}% (required: {job.test_passing_score}%)

Next steps:
1. Review the attached offer letter carefully.
2. Sign and return the offer letter within 5 business days to accept.
3. Once we receive your acceptance, our HR team will contact you with onboarding details, joining date confirmation and required documents.

If you have any questions, simply reply to this email.

Welcome aboard!

Best regards,
HR Team
{company}"""
    return subject, body


def build_test_rejection_email(candidate: Candidate, job: Job) -> tuple[str, str]:
    company = company_name()
    subject = f"Application Update - {job.title} at {company}"
    body = f"""Dear {candidate.name},

Thank you for completing the technical assessment for the {job.title} position at {company}.

Your assessment score was {candidate.test_score}%, while the minimum required score for this role is {job.test_passing_score}%. We are therefore unable to proceed with your application at this time.

We appreciate your time and interest and wish you success in your future endeavors.

Regards,
HR Team
{company}"""
    return subject, body


def _log(db: Session, candidate: Candidate, status: str, message: str, error: str | None = None):
    db.add(WorkflowLog(
        candidate_id=candidate.id,
        candidate_email=candidate.email,
        workflow_name="Decision Notification",
        status=status,
        message=message,
        test_score=candidate.test_score,
        application_status=candidate.application_status.value,
        error_message=error,
    ))
    db.commit()


def notify_test_decision(db: Session, candidate: Candidate, job: Job, n8n_payload: dict) -> dict:
    """Hands the decision to n8n; falls back to direct Gmail SMTP when n8n is unreachable.

    Returns {"channel": "n8n" | "smtp" | "none", "email_sent": bool | None, "error": str | None}.
    Status only advances to OFFER_SENT once an offer email is actually sent.
    """
    selected = candidate.application_status == ApplicationStatus.SELECTED
    subject, body = (build_acceptance_email if selected else build_test_rejection_email)(candidate, job)
    n8n_payload = {**n8n_payload, "email_subject": subject, "email_body": body}

    if trigger_n8n_test_result_webhook(n8n_payload):
        _log(db, candidate, "HANDED_TO_N8N", "Decision sent to n8n test-result workflow for email delivery.")
        return {"channel": "n8n", "email_sent": None, "error": None}

    attachment = None
    if selected:
        attachment = generate_offer_letter_pdf(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            job_title=job.title,
        )

    sent = send_email_via_gmail(to_email=candidate.email, subject=subject, body=body, attachment_path=attachment)

    if sent:
        if selected:
            candidate.application_status = ApplicationStatus.OFFER_SENT
            db.commit()
        _log(db, candidate, "EMAIL_SENT", f"{'Acceptance' if selected else 'Rejection'} email sent via Gmail SMTP.")
        return {"channel": "smtp", "email_sent": True, "error": None}

    error = "n8n unreachable and Gmail SMTP send failed (check GMAIL_USER / GMAIL_APP_PASSWORD)."
    logger.error(f"Decision email not delivered to {candidate.email}: {error}")
    _log(db, candidate, "EMAIL_FAILED", f"{'Acceptance' if selected else 'Rejection'} email NOT delivered.", error)
    return {"channel": "none", "email_sent": False, "error": error}
