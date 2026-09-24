# Implementation Plan - AI-Powered Automated Recruitment System using n8n

Build an end-to-end **AI-powered recruitment automation system** combining **n8n** (workflow automation engine), **Google Gemini AI** (resume analysis), **FastAPI** (Python backend), **React.js + Tailwind CSS** (online test platform & HR dashboard), and **MySQL** (relational database).

## User Review Required

> [!IMPORTANT]
> The system requires credentials for Gmail (OAuth2/App Password), Google Gemini API, and MySQL. Environment variables and n8n credentials placeholders are used to keep all secrets safe.
> The n8n workflows will be exported as importable JSON files (`n8n/resume-screening-workflow.json` and `n8n/test-result-workflow.json`).

> [!TIP]
> The system includes dual-trigger capabilities for n8n: direct Gmail polling and HTTP Webhook triggers, allowing you to test the workflow locally without active email infrastructure if desired.

## Open Questions

None at this time. All functional rules, score thresholds (Resume match $\ge 70\%$, Test score $\ge 80\%$), stack choices (FastAPI + MySQL + React + Tailwind + n8n + Gemini), and architectural requirements have been strictly defined.

---

## Proposed Changes

### Database & Configuration

#### [NEW] [schema.sql](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/database/schema.sql)
- Defines tables for `jobs`, `candidates`, `test_results`, and `workflow_logs`.
- Includes indexes on `candidate_email`, `test_token`, and composite unique constraint on `(email, job_id)` for duplicate application prevention.

#### [NEW] [.env.example](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/backend/.env.example)
- Configuration template for MySQL credentials, Gemini API key, Gmail settings, JWT/token secrets, frontend/backend base URLs, and n8n webhook URLs.

---

### Backend (FastAPI + SQLAlchemy + MySQL)

#### [NEW] [main.py](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/backend/app/main.py)
- FastAPI application initialization, CORS setup, router mounting, database table creation hook.

#### [NEW] [database.py](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/backend/app/database.py)
- SQLAlchemy database connection engine, session maker, and declarative base.

#### [NEW] [models](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/backend/app/models)
- `models/job.py`, `models/candidate.py`, `models/test_result.py`, `models/workflow_log.py` ORM mappings.

#### [NEW] [schemas](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/backend/app/schemas)
- Pydantic models for Candidate creation, Job config, Test verification, Test submission, Webhook payloads, and Dashboard stats.

#### [NEW] [routes](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/backend/app/routes)
- `candidates.py`: Candidate registration, lookup, duplicate checks, test token generation.
- `test.py`: Secure test token verification (`/api/test/{token}`) and candidate test submission (`/api/test/{token}/submit`).
- `webhooks.py`: `POST /api/webhooks/test-result` handling test submission webhooks for n8n.
- `jobs.py`: Endpoints for managing job descriptions (`/api/jobs`).
- `dashboard.py`: Endpoint for HR dashboard statistics (`/api/dashboard/stats`).

#### [NEW] [services/pdf_generator.py](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/backend/app/services/pdf_generator.py)
- ReportLab-based dynamic PDF offer letter generator creating styled PDF offer documents.

#### [NEW] [requirements.txt](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/backend/requirements.txt)
- FastAPI, Uvicorn, SQLAlchemy, PyMySQL, Pydantic, ReportLab, Python-dotenv, Requests, PyPDF2/python-docx for resume parsing assistance.

---

### n8n Workflows

#### [NEW] [resume-screening-workflow.json](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/n8n/resume-screening-workflow.json)
- Importable n8n workflow JSON:
  1. Gmail Trigger / Webhook Trigger
  2. Resume attachment text extraction
  3. Job Description fetch
  4. Google Gemini API integration with structured prompt
  5. JSON validation & threshold check (`match_score >= 70%`)
  6. Rejection email flow (Ineligible)
  7. Candidate record creation + Secure token test link generation + Candidate test email flow (Eligible).

#### [NEW] [test-result-workflow.json](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/n8n/test-result-workflow.json)
- Importable n8n workflow JSON:
  1. Webhook trigger (`/webhook/test-result`)
  2. Candidate status validation
  3. IF `test_score >= 80%`:
     - YES $\rightarrow$ Generate Offer Letter PDF $\rightarrow$ Send Offer Email $\rightarrow$ Update status `OFFER_SENT`.
     - NO $\rightarrow$ Update status `TEST_FAILED` $\rightarrow$ Send Rejection Email.

#### [NEW] [n8n README](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/n8n/README.md)
- Complete step-by-step guide to importing the workflows into n8n, setting up credentials (`GMAIL_CREDENTIAL_ID`, `GEMINI_CREDENTIAL_ID`, `MYSQL_CREDENTIAL_ID`), and configuring webhook endpoints.

---

### Frontend (React.js + Tailwind CSS)

#### [NEW] [frontend components & pages](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/frontend)
- **Vite React setup with Tailwind CSS**.
- `src/pages/LandingPage.jsx`: Public landing page explaining the recruitment workflow.
- `src/pages/CandidateTestPage.jsx`: Online test UI with candidate validation, countdown timer (30 mins), styled question cards (Python, SQL, ML, FastAPI, Pandas, NumPy, Logical Reasoning), and submit mechanism.
- `src/pages/TestResultPage.jsx`: Candidate test submission confirmation page.
- `src/pages/AdminDashboardPage.jsx`: HR Dashboard featuring metric cards, status breakdown charts, candidate table with filter/search, and candidate detail modal.

---

### Docker & Documentation

#### [NEW] [docker-compose.yml](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/docker-compose.yml)
- Docker Compose configuration orchestrating MySQL, FastAPI backend, React frontend, and n8n services.

#### [NEW] [README.md](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/README.md) & [architecture.md](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/docs/architecture.md)
- Detailed README covering installation, environment variable configuration, workflow import, n8n setup, test execution, troubleshooting, and full architecture diagrams.

#### [NEW] [sample_data & sample_resumes](file:///c:/Users/heeya/OneDrive/Documents/TOPS/Machine%20Learning/project/sample_data)
- Sample Job Description JSON, sample qualifying resume text/PDF, sample non-qualifying resume, sample offer letter.

---

## Verification Plan

### Automated Verification
1. **Backend Unit & Integration API Tests**: Validate FastAPI endpoints (`/api/jobs`, `/api/candidates`, `/api/test/{token}`, `/api/webhooks/test-result`, `/api/dashboard/stats`).
2. **Offer Letter PDF Generation**: Verify PDF file creation, structure, and formatting.
3. **Database Schema Verification**: Verify database migrations and constraints.

### Manual Verification
1. **n8n Workflow Validation**: Import exported JSON files into n8n, check node links, credential references, and structure.
2. **Frontend UI Walkthrough**: Test candidate assessment flow, timer behavior, token validation, test submission, and HR Admin dashboard interface.
3. **End-to-End Scenario Verification**:
   - Case 1: High resume match score ($\ge 70\%$) $\rightarrow$ Test link generated.
   - Case 2: Low resume match score ($< 70\%$) $\rightarrow$ Rejection email triggered.
   - Case 3: Candidate score $< 80\%$ on test $\rightarrow$ Test rejection email triggered.
   - Case 4: Candidate score $\ge 80\%$ on test $\rightarrow$ Offer letter PDF generated & offer email sent.
