from pydantic import BaseModel
from typing import List
from app.schemas.candidate import CandidateResponse

class DashboardStatsResponse(BaseModel):
    total_applications: int
    shortlisted: int
    rejected: int
    tests_sent: int
    tests_completed: int
    selected: int
    offers_sent: int
    recent_candidates: List[CandidateResponse]
