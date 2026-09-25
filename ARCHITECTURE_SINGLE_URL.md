# Architecture: Single Render URL Deployment

## Overview

The entire application (frontend + backend + database) runs on a **single Render URL**:

```
https://recruitment-app-xxxx.onrender.com
├── / → serves React app (frontend/dist/index.html)
├── /admin → serves React app (SPA routing)
├── /test/:token → serves React app (SPA routing)
└── /api/* → backend API endpoints
```

---

## How It Works

### 1. Build Phase (Render)

When you push to GitHub, Render automatically:

```bash
# Build the frontend React app
cd frontend
npm install
npm run build  # Creates frontend/dist/

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### 2. Deployment Phase (Render)

```bash
# Start the backend service with gunicorn
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### 3. Request Routing

FastAPI (`backend/app/main.py`) handles all requests:

```python
# API requests
GET /api/jobs → Backend returns JSON
POST /api/candidates/screen → Backend processes

# Frontend requests
GET / → Serve frontend/dist/index.html (React SPA)
GET /admin → Serve frontend/dist/index.html
GET /test/:token → Serve frontend/dist/index.html (React handles routing)
GET /assets/* → Serve React build assets
```

### 4. Database (PostgreSQL)

Render auto-creates PostgreSQL database and sets `DATABASE_URL` env var:

```
Backend ← PostgreSQL ← Render
```

---

## File Structure

```
n8n/
├── backend/
│   ├── app/
│   │   ├── main.py               # Serves both API + frontend static files
│   │   ├── routes/               # API endpoints (/api/*)
│   │   └── models/               # Database models
│   ├── Dockerfile                # Uses gunicorn in production
│   └── requirements.txt           # Includes gunicorn + psycopg2
├── frontend/
│   ├── src/                      # React source
│   ├── dist/                     # Built files (created by npm run build)
│   ├── vite.config.js            # Vite build config
│   └── package.json
├── render.yaml                   # Render blueprint (ONE service config)
└── nginx/                        # (Optional, for self-hosted setup)
```

---

## Key Changes from Separate Deployment

### Backend Changes

**`backend/app/main.py`** now serves static files:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount frontend assets
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"))
    
    # Serve index.html for all non-API routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith(("docs", "openapi", "api")):
            return None
        return FileResponse(frontend_dist / "index.html")
```

### Frontend Changes

**`frontend/src/services/api.js`** uses same-domain API calls:

```javascript
// In production (same Render domain), use same origin
// In development (localhost), use localhost:8000
const API_BASE_URL = (() => {
  const env = import.meta.env.VITE_BACKEND_URL;
  if (env) return env;
  
  if (window.location.hostname === 'localhost') {
    return 'http://localhost:8000';
  }
  
  return window.location.origin; // Production: same domain
})();
```

### CORS Configuration

No CORS needed in production (same domain):

```python
if env == "production":
    origins = ["*"]  # Frontend served from same origin
else:
    origins = ["*"]  # Development: allow all for localhost dev server
```

---

## Deployment Configuration

### `render.yaml` (Blueprint)

```yaml
services:
  - type: web
    name: recruitment-app
    runtime: python
    buildCommand: |
      cd backend && pip install -r requirements.txt && cd .. && \
      cd frontend && npm install && npm run build && cd ..
    startCommand: cd backend && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
    
  - type: pserv
    name: recruitment-db
    plan: free
    postgresVersion: 15

databases:
  - name: recruitment_db
    databaseName: recruitment_db
    user: recruitment_user
```

---

## Request Flow Diagram

```
User Browser Request
        ↓
   Render (Single Domain)
        ├─ Frontend Requests (/)
        │  └─ FastAPI static file handler
        │     └─ Serves frontend/dist/index.html
        │        └─ React app loads and handles SPA routing
        │
        └─ API Requests (/api/*)
           └─ FastAPI API routes
              └─ Process business logic
              └─ Query PostgreSQL
              └─ Return JSON
```

---

## Environment Variables

Set these in Render dashboard:

```
GEMINI_API_KEY          # Google Gemini key
GMAIL_USER              # Gmail address
GMAIL_APP_PASSWORD      # Gmail app password
COMPANY_NAME            # Company name
ENV                     # "production" (auto-set by render.yaml)
N8N_TEST_RESULT_WEBHOOK_URL  # (Optional) n8n webhook
```

Render auto-sets:

```
DATABASE_URL            # PostgreSQL connection string
FRONTEND_URL            # (Auto-set from Render domain)
BACKEND_URL             # (Auto-set from Render domain)
```

---

## Local Development

Frontend and backend run on **separate** ports locally, but Render combines them:

```bash
# Terminal 1: Backend (port 8000)
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload

# Terminal 2: Frontend (port 5173)
cd frontend
npm run dev
```

The frontend dev server has a proxy configured that sends `/api/*` requests to `localhost:8000`.

---

## Production vs Development

| Aspect | Development | Production |
|---|---|---|
| **URL** | localhost:3000 + localhost:8000 | https://recruitment-app-xxxx.onrender.com |
| **Frontend** | Vite dev server | Static files on Render |
| **Backend** | Uvicorn (single worker) | Gunicorn (4 workers) |
| **Database** | SQLite (local) or MySQL | PostgreSQL (Render) |
| **CORS** | Enabled | Same domain (not needed) |
| **Deployment** | Manual (`npm run dev` + `uvicorn`) | Automatic (git push) |

---

## Benefits of Single URL

1. **Simpler Deployment**: One Render service instead of multiple
2. **No CORS Issues**: Frontend and backend on same domain
3. **Automatic Rebuilds**: Push to Git, Render rebuilds everything
4. **Cost Efficient**: Fewer services to pay for
5. **Easy Scaling**: Render auto-scales single service
6. **No API URL Configuration**: No need to set `VITE_BACKEND_URL`

---

## Security Considerations

- Frontend app is served as static files (HTML, CSS, JS)
- API keys stored in Render env vars (not in code)
- PostgreSQL connection string from Render
- HTTPS auto-configured on Render domain
- Same-origin requests (no CORS attacks)

---

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| Blank page | Frontend not built | Check build log in Render |
| API 404 | Backend not serving | Check `/api/jobs` endpoint |
| CORS error | Shouldn't happen | Check if it's same domain |
| Database error | Connection failed | Check DATABASE_URL in env vars |

---

## Summary

This architecture simplifies deployment by combining frontend and backend on a single Render service. The frontend is built to static files during deployment, and FastAPI serves both the static files and the API endpoints from the same domain. Everything stays synchronized because it's all built and deployed together.
