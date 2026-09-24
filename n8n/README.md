# n8n Recruitment Workflows Guide

This directory contains production-ready, importable n8n workflow JSON files for automating candidate screening and test evaluation.

## Workflow 1 — Resume Screening (`resume-screening-workflow.json`)

**Trigger**: Gmail Inbox (`hr@company.com`) or Webhook `POST /webhook/resume-screening`  
**Flow**:
1. Receives candidate email with resume.
2. Extracts resume text and normalized candidate metadata.
3. Loads job description configuration.
4. Sends resume & job description to Google Gemini AI for evaluation.
5. Parses structured JSON response (`eligible`, `match_score`, `matched_skills`, `missing_skills`).
6. If `match_score >= 70%`:
   - Registers candidate as `RESUME_SHORTLISTED` in FastAPI backend (`POST /api/candidates/screen`).
   - Receives unique secure test link (`/test/<secure-token>`).
   - Sends candidate test invitation email via Gmail.
7. If `match_score < 70%`:
   - Registers candidate as `RESUME_REJECTED` in FastAPI backend.
   - Sends polite rejection email via Gmail.

---

## Workflow 2 — Test Result Evaluation (`test-result-workflow.json`)

**Trigger**: Webhook `POST /webhook/test-result`  
**Flow**:
1. Receives test submission payload from candidate test system.
2. Checks candidate score against target passing threshold (80%).
3. If `test_score >= 80%`:
   - Triggers FastAPI offer letter PDF generator (`POST /api/webhooks/test-result`).
   - Updates candidate application status to `SELECTED` and `OFFER_SENT`.
   - Sends congratulations email with attached offer letter PDF via Gmail.
4. If `test_score < 80%`:
   - Updates candidate application status to `TEST_FAILED`.
   - Sends test rejection email via Gmail.

---

## How to Import Workflows into n8n

1. Open your n8n dashboard (e.g., `http://localhost:5678`).
2. Click **Workflows** $\rightarrow$ **Add Workflow**.
3. In the top right menu, click **Import from File**.
4. Select `resume-screening-workflow.json` or `test-result-workflow.json`.

---

## Setting up Credentials in n8n

Replace the placeholder credential IDs in nodes with your actual n8n credentials:

### 1. Gmail OAuth2 Credential (`GMAIL_CREDENTIAL_ID`)
- Go to **Credentials** $\rightarrow$ **New Credential** $\rightarrow$ **Gmail OAuth2 API**.
- Authenticate with your HR Gmail account (`hr@company.com`).

### 2. Google Gemini API Key
- Set the environment variable `GEMINI_API_KEY` in n8n or replace `{{ $env.GEMINI_API_KEY }}` in the Gemini HTTP node query parameter with your key.

### 3. FastAPI Base URL
- The workflows default to `http://localhost:8000`. Adjust to your production backend URL if deployed remotely.
