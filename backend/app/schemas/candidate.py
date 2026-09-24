from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime

class CandidateCreate(BaseModel):
    name: str
    email: str
    job_id: str
    resume_filename: Optional[str] = None
    resume_text: Optional[str] = None
    resume_score: Optional[int] = 0
    resume_analysis: Optional[Dict[str, Any]] = None

class CandidateScreeningUpdate(BaseModel):
    email: str
    job_id: str
    name: Optional[str] = None
    resume_score: int
    eligible: bool
    resume_analysis: Optional[Dict[str, Any]] = None
    resume_text: Optional[str] = None

class CandidateResponse(BaseModel):
    id: int
    candidate_id: str
    name: str
    email: str
    job_id: str
    resume_score: int
    resume_analysis: Optional[Dict[str, Any]] = None
    test_token: Optional[str] = None
    test_status: str
    test_score: int
    application_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
