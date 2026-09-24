
# Architecture Documentation — AI Recruitment Automation

This document outlines the system architecture, sequence flow, data schemas, and API contracts for the **AI-Powered Automated Recruitment System using n8n**.

---

## 1. High-Level Workflow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Candidate
    participant Gmail as HR Gmail
    participant n8n as n8n Engine
    participant Gemini as Google Gemini AI
    participant API as FastAPI Backend
    participant DB as MySQL Database
    participant React as React Assessment UI

    Candidate->>Gmail: Send Email + Resume (candidate_resume.pdf)
    Gmail->>n8n: Gmail Trigger (Polls or Push)
    n8n->>n8n: Read Email & Extract Resume Text
    n8n->>Gemini: Prompt with Job Description + Resume Text
    Gemini-->>n8n: Structured JSON (eligible, match_score, breakdown)
    
    alt match_score < 70 (Ineligible)
        n8n->>API: POST /api/candidates/screen (eligible: false)
        API->>DB: Log candidate as RESUME_REJECTED
        n8n->>Gmail: Send Rejection Email
    else match_score >= 70 (Eligible)
        n8n->>API: POST /api/candidates/screen (eligible: true)
        API->>DB: Store Candidate & Generate Secure Test Token
        API-->>n8n: Return Test Link (/test/:token)
        n8n->>Gmail: Send Test Link Email to Candidate
        
        Candidate->>React: Open /test/:token Link
        React->>API: GET /api/test/:token (Verify Token)
        API-->>React: Return Questions & Candidate Info
        Candidate->>React: Complete MCQ & Click Submit
        React->>API: POST /api/test/:token/submit
        API->>DB: Store Test Score & Answers
        API->>n8n: Webhook POST /webhook/test-result
        
        alt test_score >= 80% (Passed)
            API->>API: Generate Offer Letter PDF
            API->>DB: Update status to SELECTED & OFFER_SENT
            n8n->>Gmail: Send Offer Letter Email + PDF Attachment
        else test_score < 80% (Failed)
            API->>DB: Update status to TEST_FAILED
            n8n->>Gmail: Send Assessment Rejection Email
        end
    end
```

---

## 2. Key Components

### Workflow Automation (n8n)
- **Resume Screening Workflow**: Polls HR Gmail inbox, parses resume documents (PDF/DOCX/TXT), queries Google Gemini AI, and branches logic based on Gemini's match score ($\ge 70\%$).
- **Test Evaluation Workflow**: Receives test submission webhooks (`/webhook/test-result`), checks passing threshold ($\ge 80\%$), triggers PDF offer generation, and sends offer or rejection emails.

### FastAPI Backend
- Serves CRUD endpoints for Job Descriptions and Candidate applications.
- Manages secure candidate token generation and verification.
- Calculates test scores and updates MySQL database records.
- Dynamically generates styled PDF offer letters using ReportLab.

### React + Tailwind CSS Frontend
- **Candidate Assessment Platform**: Timed 30-minute online MCQ exam interface with token validation.
- **HR Admin Dashboard**: Visual real-time metric cards, candidate status pipeline, filter/search controls, and Gemini AI score analysis modals.

### MySQL Database
- Schema contains tables for `jobs`, `candidates`, `test_results`, and `workflow_logs`.
