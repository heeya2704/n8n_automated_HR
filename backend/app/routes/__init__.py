from app.routes.jobs import router as jobs_router
from app.routes.candidates import router as candidates_router
from app.routes.test import router as test_router
from app.routes.webhooks import router as webhooks_router
from app.routes.dashboard import router as dashboard_router
from app.routes.gmail import router as gmail_router

__all__ = [
    "jobs_router", 
    "candidates_router", 
    "test_router", 
    "webhooks_router", 
    "dashboard_router",
    "gmail_router"
]
