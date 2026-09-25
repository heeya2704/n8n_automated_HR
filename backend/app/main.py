import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Configure CORS based on environment
env = os.getenv("ENV", "development")
if env == "production":
    # In production, frontend and backend are on the same domain (single Render URL)
    # No CORS needed, but allow same-origin requests
    origins = ["*"]  # Frontend is served from same origin
else:
    # Development: allow localhost frontend to talk to localhost backend
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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

# Mount Routes
app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(test_router)
app.include_router(webhooks_router)
app.include_router(dashboard_router)
app.include_router(gmail_router)

# API health check
@app.get("/")
def root():
    return {
        "system": "AI-Powered Automated Recruitment System",
        "status": "online",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

# Serve frontend static files (built React app)
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    # Serve all other routes with index.html (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve SPA - return index.html for all non-API routes"""
        # Don't override /docs, /openapi.json, /api/* routes
        if full_path.startswith(("docs", "openapi", "api", "favicon.ico")):
            return None

        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Frontend not built"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
