from sqlalchemy import Column, String, Text, JSON, Integer, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=False)
    minimum_experience = Column(String(100), default="0-2 years")
    minimum_resume_score = Column(Integer, default=70)
    test_passing_score = Column(Integer, default=80)
    created_at = Column(DateTime, server_default=func.now())

    candidates = relationship("Candidate", back_populates="job")
