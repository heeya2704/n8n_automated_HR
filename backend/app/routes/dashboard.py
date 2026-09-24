from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Candidate, ApplicationStatus
from app.schemas import DashboardStatsResponse, CandidateResponse

router = APIRouter(prefix="/api/dashboard", tags=["HR Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_statistics(db: Session = Depends(get_db)):
    """
    Computes real-time statistics and metrics for the HR Admin Dashboard.
    """
    all_candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()

    total_applications = len(all_candidates)
    
    shortlisted = sum(
        1 for c in all_candidates 
        if c.application_status in [
            ApplicationStatus.RESUME_SHORTLISTED, 
            ApplicationStatus.TEST_SENT,
            ApplicationStatus.TEST_STARTED,
            ApplicationStatus.TEST_COMPLETED,
            ApplicationStatus.SELECTED,
            ApplicationStatus.OFFER_SENT
        ]
    )

    rejected = sum(
        1 for c in all_candidates 
        if c.application_status in [
            ApplicationStatus.RESUME_REJECTED, 
            ApplicationStatus.TEST_FAILED
        ]
    )

    tests_sent = sum(
        1 for c in all_candidates 
        if c.application_status in [
            ApplicationStatus.TEST_SENT,
            ApplicationStatus.TEST_STARTED,
            ApplicationStatus.TEST_COMPLETED,
            ApplicationStatus.SELECTED,
            ApplicationStatus.OFFER_SENT
        ] or c.test_token is not None
    )

    tests_completed = sum(
        1 for c in all_candidates 
        if c.application_status in [
            ApplicationStatus.TEST_COMPLETED,
            ApplicationStatus.TEST_FAILED,
            ApplicationStatus.SELECTED,
            ApplicationStatus.OFFER_SENT
        ]
    )

    selected = sum(
        1 for c in all_candidates 
        if c.application_status in [
            ApplicationStatus.SELECTED,
            ApplicationStatus.OFFER_SENT
        ]
    )

    offers_sent = sum(
        1 for c in all_candidates 
        if c.application_status == ApplicationStatus.OFFER_SENT
    )

    recent_candidates = [CandidateResponse.model_validate(c) for c in all_candidates[:20]]

    return DashboardStatsResponse(
        total_applications=total_applications,
        shortlisted=shortlisted,
        rejected=rejected,
        tests_sent=tests_sent,
        tests_completed=tests_completed,
        selected=selected,
        offers_sent=offers_sent,
        recent_candidates=recent_candidates
    )
