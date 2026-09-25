# AI-Powered Automated Recruitment System using n8n

An end-to-end recruitment automation solution powered by **n8n**, **Google Gemini AI**, **FastAPI**, **React.js + Tailwind CSS**, and **MySQL**.

---

## 1. Project Overview

This system automates the entire candidate recruitment funnel:
1. **Candidate emails a resume** (PDF) to the HR Gmail inbox.
2. **n8n Gmail Trigger** (or the backend's Gmail IMAP sync) picks it up and extracts the resume text.
3. **Google Gemini AI** scores the resume against the job's description and required skills.
4. **Resume screening** uses each job's own `minimum_resume_score` (default 70). The rule is `score >= threshold`, so a score exactly at the threshold passes.
   - Below the threshold: status `RESUME_REJECTED`, rejection email.
   - At or above it: status `RESUME_SHORTLISTED`, secure 48-hour test link emailed.
5. **Online assessment:** a timed 30-minute MCQ test at `/test/<token>`.
6. **Final decision** uses the job's `test_passing_score` (default 80).
   - Below it: status `TEST_FAILED`, assessment rejection email.
   - At or above it: status `SELECTED`. The acceptance email with the offer letter PDF and next steps goes out, then the status becomes `OFFER_SENT`.
7. **HR Admin Dashboard** (`/admin`): candidates, applied job, Gemini and test scores, status (Rejected, Selected · Offer pending, Selected · Offer sent), AI analysis, resume view/download, offer letter PDF.

---

## 2. Technology Stack

- **Automation Engine**: n8n
- **AI Model**: Google Gemini API (`gemini-3.6-flash`, configurable via `GEMINI_MODEL`)
- **Backend API**: Python 3.10+, FastAPI, SQLAlchemy, ReportLab (PDF Generation)
- **Frontend UI**: React.js, Tailwind CSS, Lucide Icons, Vite
- **Database**: MySQL 8.0
- **Containerization**: Docker & Docker Compose

---

## 3. Project Structure

```text
ai-recruitment-automation/
│
├── n8n/
│   ├── resume-screening-workflow.json   # Importable n8n resume screening workflow
│   ├── test-result-workflow.json        # Importable n8n test result workflow
│   └── README.md                        # n8n setup & credential guide
│
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI application entry point
│   │   ├── database.py                  # SQLAlchemy engine & session maker
│   │   ├── models/                      # SQLAlchemy ORM models (Job, Candidate, TestResult, Log)
│   │   ├── schemas/                     # Pydantic request/response schemas
│   │   ├── routes/                      # API endpoints (candidates, test, webhooks, jobs, dashboard)
│   │   ├── services/                    # PDF offer generator & n8n webhook client
│   │   └── utils/                       # Resume text parser (PDF/DOCX/TXT)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/                  # Navbar, Footer
│   │   ├── pages/                       # LandingPage, CandidateTestPage, TestResultPage, AdminDashboardPage
│   │   ├── services/                    # Axios API client
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css                    # Tailwind + Glassmorphism design system
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── .env.example
│
├── database/
│   └── schema.sql                       # MySQL schema & default seed job
│
├── sample_data/
│   ├── job_description.json             # Sample Python/ML Job Description
│   ├── sample_resume_eligible.txt       # Qualifying candidate sample resume
│   └── sample_resume_ineligible.txt     # Non-qualifying candidate sample resume
│
├── offer-letters/                       # Generated offer letter PDFs
├── docs/
│   └── architecture.md                  # System architecture & Mermaid sequence diagram
├── docker-compose.yml
└── README.md
```

---

## 4. Environment Variables

Copy the examples and fill in your keys:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

Key settings in `backend/.env`:

| Variable | Purpose |
|---|---|
| `USE_SQLITE=true` | Zero-setup local DB (`backend/recruitment.db`). Set `false` to use `DATABASE_URL` (MySQL). |
| `GEMINI_API_KEY` | Google Gemini API key (required for resume scoring). |
| `GEMINI_MODEL` | Optional, default `gemini-3.6-flash`. |
| `GMAIL_USER`, `GMAIL_APP_PASSWORD` | Gmail address + 16-char App Password (IMAP sync + SMTP fallback emails). |
| `N8N_TEST_RESULT_WEBHOOK_URL` | n8n test-result webhook (default `http://localhost:5678/webhook/test-result`). |
| `FRONTEND_URL` | Used to build candidate test links. |
| `BACKEND_URL` | Used to build the offer-letter download URL that n8n fetches. |
| `COMPANY_NAME` | Company name used in emails. |

`backend/.env` is git-ignored. Never commit it.

`frontend/.env`: `VITE_BACKEND_URL="http://localhost:8000"`

Thresholds are **per job** (`minimum_resume_score`, `test_passing_score`) and set when creating a job:

```bash
curl -X POST http://localhost:8000/api/jobs -H "Content-Type: application/json" -d '{"id":"data-analyst-001","title":"Data Analyst","description":"SQL and dashboards","required_skills":["SQL","Excel","Power BI"],"minimum_experience":"0-2 years","minimum_resume_score":75,"test_passing_score":70}'
```

---

## 5. How to Run (Windows, local, no Docker)

**Prerequisites:** Python 3.10+ and Node.js 18+.

### First-time setup

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### Start the project (two terminals)

**Terminal 1: backend API** (http://localhost:8000, docs at http://localhost:8000/docs)

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2: frontend** (http://localhost:3000, HR panel at http://localhost:3000/admin)

```powershell
cd frontend
npm run dev
```

**Optional, Terminal 3: n8n** (http://localhost:5678)

```powershell
$env:GEMINI_API_KEY="your_key"; $env:N8N_BLOCK_ENV_ACCESS_IN_NODE="false"; npx n8n
```

Then import the workflows as described in [n8n/README.md](n8n/README.md). n8n is optional for local runs. Without it, the backend sends the decision emails directly via Gmail SMTP.

### Run the automated tests

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests -q
```

The tests cover: rejection at screening, the selection path with acceptance email, a score exactly at the threshold, different thresholds per job, email failure handling, duplicate submissions, and Gemini outages. Gemini, n8n and Gmail are mocked, so no real emails are sent.

### Option B: Docker Compose (MySQL + backend + frontend + n8n)

Start Docker Desktop, create a root `.env` with `GEMINI_API_KEY`, `GMAIL_USER` and `GMAIL_APP_PASSWORD`, then:

```bash
docker compose up -d --build
```

---

## 6. Email Delivery & Status Flow

```
RECEIVED -> RESUME_REJECTED                                      (rejection email)
         -> RESUME_SHORTLISTED -> TEST_STARTED -> TEST_FAILED    (assessment rejection email)
                                               -> SELECTED -> OFFER_SENT   (acceptance email + offer PDF)
```

- After test submission the backend decides the outcome, then hands email delivery to n8n.
- If n8n is unreachable, the backend sends the email itself over Gmail SMTP.
- `OFFER_SENT` is set **only after** the acceptance email is actually sent: by n8n calling `POST /api/webhooks/offer-sent`, or by a successful SMTP send.
- If the email fails, the candidate stays `SELECTED` ("Offer pending" in the HR panel) and an `EMAIL_FAILED` entry is written to `workflow_logs`.
- Re-submitting a resume for the same job is ignored (`DUPLICATE`). Duplicate records and repeat emails are prevented.
- If Gemini fails, the candidate is **not** rejected. The API returns 502, and the n8n workflow errors instead of sending a rejection email.

Useful endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /api/candidates/screen` | Store the Gemini score and apply the job threshold. Returns SHORTLISTED, REJECTED or DUPLICATE. |
| `POST /api/candidates/screen-resume` | Score resume text with Gemini directly, then screen it. |
| `POST /api/gmail/sync-inbox` | Pull resumes from Gmail (IMAP), screen them, email results. |
| `GET /api/candidates/{id}/resume` | Resume text for HR. |
| `GET /api/candidates/{id}/offer-letter` | Offer letter PDF (selected candidates only). |
| `POST /api/webhooks/offer-sent` | n8n confirms the acceptance email was delivered. |
| `GET /api/dashboard/stats` | HR dashboard data. |

---

## 7. Testing the Complete Workflow Manually

1. Start the backend and frontend (section 5).
2. Screen a candidate without Gmail or n8n, using real Gemini:
   ```powershell
   $resume = Get-Content sample_data\sample_resume_eligible.txt -Raw
   Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/candidates/screen-resume?name=Jane%20Doe&email=you@example.com&job_id=python-ml-developer-001" -ContentType "application/json" -Body ($resume | ConvertTo-Json)
   ```
   The response contains `status` (`SHORTLISTED` or `REJECTED`) and a `test_link`.
3. Open the `test_link`, answer the questions and submit.
4. Open http://localhost:3000/admin. The candidate shows **Selected · Offer sent**, **Selected · Offer pending** (email not delivered yet) or **Rejected · Test**. Click the row to see the AI analysis, the resume and the offer letter PDF.

Note: `screen-resume` itself does not send email. The acceptance/rejection email after the test is sent via n8n or the SMTP fallback, so use your own address when testing.

---

## 8. Production Deployment (Single Render URL)

**Deploy everything on ONE URL** — frontend + backend + database on the same Render service.

See [DEPLOY_SINGLE_URL.md](DEPLOY_SINGLE_URL.md) for the complete 5-minute guide.

### Quick Overview

| Component | Where | Cost |
|---|---|---|
| Frontend (React app) | Render static files | Included |
| Backend (FastAPI API) | Render service | $7–15/mo |
| Database (PostgreSQL) | Render | $15+/mo |
| Total | Single URL | ~$22–30/mo |

### Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add -A && git commit -m "Deploy" && git push
   ```

2. **Deploy on Render**:
   - Go to render.com → New → Blueprint
   - Paste GitHub repo URL
   - Render reads `render.yaml` and auto-configures
   - Set env vars: `GEMINI_API_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`
   - Click Deploy → Wait 5–10 min

3. **Done**:
   - Frontend: `https://recruitment-app-xxxx.onrender.com/admin`
   - API: `https://recruitment-app-xxxx.onrender.com/api/jobs`
   - Everything on the **same domain**

### Why Single URL?

✅ **No CORS issues** — frontend and backend on same domain  
✅ **Simple deployment** — one Render service, one PostgreSQL database  
✅ **Automatic builds** — push to Git, Render rebuilds automatically  
✅ **Cost efficient** — no extra services needed  
✅ **Easy scaling** — Render handles it automatically  

### Development (Unchanged)

Local development stays the same:

```bash
# Terminal 1: Backend (http://localhost:8000)
cd backend && ./venv/Scripts/python.exe -m uvicorn app.main:app --reload

# Terminal 2: Frontend (http://localhost:3000 or 5173)
cd frontend && npm run dev
```

The frontend dev server automatically proxies `/api/*` to the backend.

---

## 9. License & Author

Developed for automated AI hiring workflow pipelines using n8n engine, FastAPI, React, and Google Gemini AI.

---

## 10. Resume & CV Project Description (Ready to Copy-Paste)

### Project Title
**AI-Powered Automated Recruitment & Candidate Screening Platform**

### Bullet Points for CV / Resume:
- **Architected an end-to-end recruitment automation pipeline** utilizing n8n, FastAPI, React.js, and Google Gemini AI to automate candidate screening, assessment link generation, and offer letter creation.
- **Implemented live Gmail integration (IMAP/SMTP)** to fetch incoming candidate resumes (PDF, DOCX, TXT) and send real-time test invitations and offer letters with dynamic PDF attachments.
- **Integrated Google Gemini AI API** with structured JSON prompt engineering to evaluate candidate skills against job requirements, computing objective match scores against configurable per-job thresholds.
- **Engineered a candidate online assessment platform** featuring secure single-use cryptographic tokens, a 30-minute timed exam UI, and instant automated grading.
- **Automated offer letter generation** using Python ReportLab to dynamically generate branded PDF offer documents for candidates meeting the job's assessment threshold.
- **Technologies**: Python, FastAPI, Google Gemini AI API, n8n, React.js, Tailwind CSS, ReportLab, SQLite, MySQL.

