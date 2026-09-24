from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    minimum_experience: Optional[str] = "0-2 years"
    minimum_resume_score: Optional[int] = 70
    test_passing_score: Optional[int] = 80

class JobCreate(JobBase):
    id: str

class JobResponse(JobBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
