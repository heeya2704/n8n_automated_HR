from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TestStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"

class ApplicationStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    RESUME_PROCESSING = "RESUME_PROCESSING"
    RESUME_REJECTED = "RESUME_REJECTED"
    RESUME_SHORTLISTED = "RESUME_SHORTLISTED"
    TEST_SENT = "TEST_SENT"
    TEST_STARTED = "TEST_STARTED"
    TEST_COMPLETED = "TEST_COMPLETED"
    TEST_FAILED = "TEST_FAILED"
    SELECTED = "SELECTED"
    OFFER_SENT = "OFFER_SENT"
    ERROR = "ERROR"

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(64), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    job_id = Column(String(64), ForeignKey("jobs.id"), nullable=False)
    resume_filename = Column(String(255), nullable=True)
    resume_text = Column(Text, nullable=True)
    resume_score = Column(Integer, default=0)
    resume_analysis = Column(JSON, nullable=True)
    test_token = Column(String(128), unique=True, nullable=True)
    test_token_expires_at = Column(DateTime, nullable=True)
    test_status = Column(Enum(TestStatus), default=TestStatus.NOT_STARTED)
    test_score = Column(Integer, default=0)
    application_status = Column(Enum(ApplicationStatus), default=ApplicationStatus.RECEIVED)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    job = relationship("Job", back_populates="candidates")
    test_results = relationship("TestResult", back_populates="candidate")

    @property
    def job_title(self):
        return self.job.title if self.job else None

    @property
    def job_minimum_resume_score(self):
        return self.job.minimum_resume_score if self.job else None
