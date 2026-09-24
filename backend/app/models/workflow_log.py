from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base

class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, nullable=True)
    candidate_email = Column(String(255), nullable=False)
    workflow_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    message = Column(Text, nullable=True)
    resume_score = Column(Integer, nullable=True)
    test_score = Column(Integer, nullable=True)
    application_status = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
