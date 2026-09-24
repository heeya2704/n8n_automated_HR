from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QuestionOption(BaseModel):
    id: str
    text: str

class QuestionItem(BaseModel):
    id: int
    category: str
    question: str
    options: List[str]

class TestVerifyResponse(BaseModel):
    valid: bool
    candidate_name: str
    candidate_email: str
    job_title: str
    time_limit_minutes: int = 30
    total_questions: int
    questions: List[QuestionItem]
    message: Optional[str] = None

class AnswerSubmission(BaseModel):
    question_id: int
    selected_option: str

class TestSubmitRequest(BaseModel):
    answers: List[AnswerSubmission]

class TestSubmitResponse(BaseModel):
    message: str
    candidate_id: str
    candidate_email: str
    score: int
    total_questions: int
    correct_answers: int
    status: str
    eligible_for_offer: bool
