import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, Base, SessionLocal
from app.models import Job
from app.routes import (
    jobs_router,
    candidates_router,
    test_router,
    webhooks_router,
    dashboard_router,
    gmail_router
)

# Initialize database tables and seed default job
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    existing_job = db.query(Job).filter(Job.id == "python-ml-developer-001").first()
    if not existing_job:
        default_job = Job(
            id="python-ml-developer-001",
            title="Python / Machine Learning Developer",
            description="We are looking for a Python/Machine Learning developer who can build APIs, work with ML models and databases, and develop automation systems.",
            required_skills=["Python", "FastAPI", "SQL", "Machine Learning", "Pandas", "NumPy", "REST API", "Git"],
            minimum_experience="0-2 years",
            minimum_resume_score=70,
            test_passing_score=80
        )
        db.add(default_job)
        db.commit()
    db.close()
except Exception as e:
    print(f"Database initialization notice: {e}")

app = FastAPI(
    title="AI-Powered Automated Recruitment System API",
    description="Backend API powering candidate screening, online assessments, n8n webhooks, and offer letter generation.",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(test_router)
app.include_router(webhooks_router)
app.include_router(dashboard_router)
app.include_router(gmail_router)

@app.get("/")
def root():
    return {
        "system": "AI-Powered Automated Recruitment System",
        "status": "online",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
