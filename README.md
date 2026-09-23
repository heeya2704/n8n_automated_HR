# AI-Powered Automated Recruitment System using n8n

An end-to-end recruitment automation solution powered by **n8n**, **Google Gemini AI**, **FastAPI**, **React.js + Tailwind CSS**, and **MySQL**.

---

## 1. Project Overview

This system automates the entire candidate recruitment funnel:
1. **Candidate Emails Resume** to HR Gmail (`hr@company.com`).
2. **n8n Gmail Trigger** detects incoming application and extracts resume text.
3. **Google Gemini AI** evaluates resume against configured Job Description and returns structured JSON analysis.
4. **Resume Eligibility Filter**:
   - If Match Score $< 70\%$: Candidate receives an automated rejection email.
   - If Match Score $\ge 70\%$: Candidate is shortlisted; FastAPI generates a cryptographically secure test token and sends an online assessment link via Gmail.
5. **Candidate Assessment Platform**: Candidate completes timed 30-minute online MCQ test.
6. **n8n Webhook Test Result Workflow**:
   - If Test Score $< 80\%$: Candidate receives assessment rejection email.
   - If Test Score $\ge 80\%$: System generates custom **Offer Letter PDF** and sends offer email with attachment.
7. **HR Admin Dashboard**: Real-time pipeline monitoring, applicant tracking, and AI match score analysis.

---

## 2. Technology Stack

- **Automation Engine**: n8n
- **AI Model**: Google Gemini API (Gemini 1.5 Flash / Gemini 3.6 Flash)
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

Create `.env` inside `backend/`:

```env
# Application Settings
APP_NAME="AI Recruitment System"
HOST="0.0.0.0"
PORT=8000

# Security
JWT_SECRET="super-secret-jwt-key"
TEST_TOKEN_EXPIRE_HOURS=48

# Database
MYSQL_HOST="localhost"
MYSQL_PORT=3306
MYSQL_USER="root"
MYSQL_PASSWORD="your_mysql_password"
MYSQL_DATABASE="recruitment_db"
DATABASE_URL="mysql+pymysql://root:your_mysql_password@localhost:3306/recruitment_db"

# Gemini AI API
GEMINI_API_KEY="your_gemini_api_key_here"

# Gmail
GMAIL_USER="hr@company.com"
GMAIL_APP_PASSWORD="your_gmail_app_password"

# URLs
FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"
N8N_TEST_RESULT_WEBHOOK_URL="http://localhost:5678/webhook/test-result"
```

Create `.env` inside `frontend/`:

```env
VITE_BACKEND_URL="http://localhost:8000"
```

---

## 5. Setup & Running Options

### Option A: Running with Docker Compose (Recommended)

Start all services (MySQL, FastAPI Backend, React Frontend, n8n) with a single command:

```bash
docker compose up -d
```

- **React Frontend**: `http://localhost:3000`
- **FastAPI API Docs**: `http://localhost:8000/docs`
- **n8n Engine**: `http://localhost:5678`
- **MySQL DB**: `localhost:3306`

---

### Option B: Local Setup Without Docker

#### 1. MySQL Setup
Import database schema into MySQL:

```bash
mysql -u root -p < database/schema.sql
```

*(Note: SQLite fallback is supported by setting `USE_SQLITE=true` in `backend/.env` for quick local testing).*

#### 2. Running FastAPI Backend

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Running React Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at `http://localhost:3000`.

---

## 6. n8n Setup & Workflow Import

1. Open n8n dashboard (`http://localhost:5678`).
2. Go to **Workflows** $\rightarrow$ **Import from File**.
3. Import `n8n/resume-screening-workflow.json` and `n8n/test-result-workflow.json`.
4. Configure Credentials:
   - **Gmail**: Add **Gmail OAuth2** credential or App Password.
   - **Gemini AI**: Set `GEMINI_API_KEY` in n8n environment variables or HTTP query parameter.

---

## 7. Testing the Complete Workflow

### Scenario 1: Qualifying Candidate (Resume Score $\ge 70\%$, Test Score $\ge 80\%$)
1. Candidate submits email/resume matching Python & Machine Learning skills.
2. Gemini evaluates match score (e.g. $87\%$).
3. Candidate receives test link email (`http://localhost:3000/test/<token>`).
4. Candidate takes 30-minute test and scores $90\%$.
5. System generates PDF offer letter and sends offer email.

### Scenario 2: Non-Qualifying Resume (Resume Score $< 70\%$)
1. Candidate submits graphic design resume.
2. Gemini evaluates match score ($40\%$).
3. Candidate receives rejection email automatically.

### Scenario 3: Candidate Fails Assessment (Test Score $< 80\%$)
1. Candidate passes resume screening ($85\%$) and receives test link.
2. Candidate scores $70\%$ on technical test (below $80\%$ threshold).
3. Candidate receives assessment rejection email.

---

## 8. License & Author

Developed for automated AI hiring workflow pipelines using n8n engine, FastAPI, React, and Google Gemini AI.

---

## 9. Resume & CV Project Description (Ready to Copy-Paste)

### Project Title
**AI-Powered Automated Recruitment & Candidate Screening Platform**

### Bullet Points for CV / Resume:
- **Architected an end-to-end recruitment automation pipeline** utilizing n8n, FastAPI, React.js, and Google Gemini AI to automate candidate screening, assessment link generation, and offer letter creation.
- **Implemented live Gmail integration (IMAP/SMTP)** to fetch incoming candidate resumes (PDF, DOCX, TXT) and send real-time test invitations and offer letters with dynamic PDF attachments.
- **Integrated Google Gemini AI API** with structured JSON prompt engineering to evaluate candidate skills against job requirements, computing objective match scores ($\ge 70\%$ threshold).
- **Engineered a candidate online assessment platform** featuring secure single-use cryptographic tokens, a 30-minute timed exam UI, and instant automated grading.
- **Automated offer letter generation** using Python ReportLab to dynamically generate branded PDF offer documents for candidates scoring $\ge 80\%$.
- **Technologies**: Python, FastAPI, Google Gemini AI API, n8n, React.js, Tailwind CSS, ReportLab, SQLite, MySQL.

