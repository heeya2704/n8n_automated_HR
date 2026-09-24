"""End-to-end API tests for the screening -> assessment -> decision -> email flow.

Gemini, n8n and Gmail are mocked, so these tests never call external services or send email.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes.test import QUESTION_BANK  # noqa: E402

ALL_CORRECT = [{"question_id": q["id"], "selected_option": q["correct_answer"]} for q in QUESTION_BANK]


def answers(n_correct):
    return [
        {"question_id": q["id"], "selected_option": q["correct_answer"] if i < n_correct else "wrong"}
        for i, q in enumerate(QUESTION_BANK)
    ]


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FRONTEND_URL", "https://portal.example.com")
    monkeypatch.setenv("BACKEND_URL", "https://api.example.com")
    monkeypatch.setenv("COMPANY_NAME", "Acme Corp")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database import Base, get_db
    from app.models import Job
    import app.services.notifications as notifications

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db

    db = Session()
    db.add(Job(id="job-70-80", title="Python Developer", description="Python APIs",
               required_skills=["Python"], minimum_resume_score=70, test_passing_score=80))
    db.add(Job(id="job-90-60", title="Senior Data Scientist", description="ML research",
               required_skills=["ML"], minimum_resume_score=90, test_passing_score=60))
    db.commit()
    db.close()

    state = {"n8n_up": False, "smtp_ok": True, "n8n_calls": [], "emails": []}

    def fake_n8n(payload):
        state["n8n_calls"].append(payload)
        return state["n8n_up"]

    def fake_send(to_email, subject, body, attachment_path=None, **kw):
        state["emails"].append({"to": to_email, "subject": subject, "body": body, "attachment": attachment_path})
        return state["smtp_ok"]

    monkeypatch.setattr(notifications, "trigger_n8n_test_result_webhook", fake_n8n)
    monkeypatch.setattr(notifications, "send_email_via_gmail", fake_send)

    client = TestClient(app)
    yield client, state, Session
    app.dependency_overrides.clear()


def screen(client, email, score, job_id="job-70-80", name="Jane Doe"):
    r = client.post("/api/candidates/screen", json={
        "email": email, "name": name, "job_id": job_id, "resume_score": score,
        "resume_text": f"Resume of {name}", "resume_filename": "cv.pdf",
        "resume_analysis": {"match_score": score, "reason": "test"},
    })
    assert r.status_code == 200, r.text
    return r.json()


def candidate(client, email):
    return next(c for c in client.get("/api/candidates").json() if c["email"] == email)


def logs(Session, email):
    from app.models import WorkflowLog
    db = Session()
    try:
        return [l.status for l in db.query(WorkflowLog).filter(WorkflowLog.candidate_email == email)]
    finally:
        db.close()


# Test A: rejected at resume screening
def test_a_resume_below_threshold_is_rejected(env):
    client, state, _ = env
    res = screen(client, "low@x.com", 40)
    assert res["status"] == "REJECTED"
    assert res["threshold"] == 70
    c = candidate(client, "low@x.com")
    assert c["application_status"] == "RESUME_REJECTED"
    assert c["test_token"] is None
    assert c["job_title"] == "Python Developer"
    stats = client.get("/api/dashboard/stats").json()
    assert stats["rejected"] == 1


# Test B: full selection path, n8n offline -> backend SMTP fallback sends acceptance email
def test_b_selected_candidate_gets_acceptance_email_via_smtp_fallback(env):
    client, state, Session = env
    res = screen(client, "star@x.com", 85, name="Star Candidate")
    assert res["status"] == "SHORTLISTED"
    assert res["test_link"].startswith("https://portal.example.com/test/")
    token = res["test_token"]

    assert client.get(f"/api/test/{token}").status_code == 200
    r = client.post(f"/api/test/{token}/submit", json={"answers": ALL_CORRECT})
    assert r.status_code == 200
    body = r.json()
    assert body["score"] == 100 and body["eligible_for_offer"] is True
    assert body["status"] == "OFFER_SENT"

    assert len(state["emails"]) == 1
    mail = state["emails"][0]
    assert mail["to"] == "star@x.com"
    assert "Python Developer" in mail["subject"] and "Acme Corp" in mail["subject"]
    assert "Dear Star Candidate" in mail["body"] and "Next steps" in mail["body"]
    assert mail["attachment"] and os.path.exists(mail["attachment"])

    c = candidate(client, "star@x.com")
    assert c["application_status"] == "OFFER_SENT"
    assert c["test_score"] == 100
    assert "EMAIL_SENT" in logs(Session, "star@x.com")
    stats = client.get("/api/dashboard/stats").json()
    assert stats["selected"] == 1 and stats["offers_sent"] == 1


# Test B (n8n path): n8n delivers email, then confirms via /offer-sent
def test_b_selected_candidate_via_n8n_and_offer_confirmation(env):
    client, state, _ = env
    state["n8n_up"] = True
    token = screen(client, "n8n@x.com", 90)["test_token"]
    body = client.post(f"/api/test/{token}/submit", json={"answers": ALL_CORRECT}).json()

    assert body["status"] == "SELECTED"
    assert state["emails"] == []
    payload = state["n8n_calls"][0]
    assert payload["eligible_for_offer"] is True
    assert payload["job_title"] == "Python Developer"
    assert "Dear Jane Doe" in payload["email_body"]
    assert payload["offer_letter_url"].startswith("https://api.example.com/api/candidates/")

    uuid = payload["candidate_uuid"]
    pdf = client.get(f"/api/candidates/{uuid}/offer-letter")
    assert pdf.status_code == 200 and pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:4] == b"%PDF"

    r = client.post("/api/webhooks/offer-sent", json={"candidate_id": uuid, "candidate_email": "n8n@x.com"})
    assert r.status_code == 200 and r.json()["status"] == "OFFER_SENT"
    again = client.post("/api/webhooks/offer-sent", json={"candidate_id": uuid})
    assert again.status_code == 200
    assert candidate(client, "n8n@x.com")["application_status"] == "OFFER_SENT"


def test_failed_assessment_sends_rejection(env):
    client, state, _ = env
    token = screen(client, "meh@x.com", 75)["test_token"]
    body = client.post(f"/api/test/{token}/submit", json={"answers": answers(5)}).json()
    assert body["score"] == 50 and body["status"] == "TEST_FAILED"
    assert state["emails"][0]["attachment"] is None
    assert "80%" in state["emails"][0]["body"]
    assert candidate(client, "meh@x.com")["application_status"] == "TEST_FAILED"
    uuid = candidate(client, "meh@x.com")["candidate_id"]
    assert client.get(f"/api/candidates/{uuid}/offer-letter").status_code == 400


# Test C: exactly at threshold passes (>=)
def test_c_scores_exactly_at_threshold_pass(env):
    client, _, _ = env
    res = screen(client, "edge@x.com", 70)
    assert res["status"] == "SHORTLISTED"
    body = client.post(f"/api/test/{res['test_token']}/submit", json={"answers": answers(8)}).json()
    assert body["score"] == 80 and body["eligible_for_offer"] is True
    assert screen(client, "edge2@x.com", 69)["status"] == "REJECTED"


# Test D: job-specific thresholds are used, not a hard-coded value
def test_d_job_specific_thresholds(env):
    client, _, _ = env
    assert screen(client, "d@x.com", 85, job_id="job-70-80")["status"] == "SHORTLISTED"
    assert screen(client, "d@x.com", 85, job_id="job-90-60")["status"] == "REJECTED"
    res = screen(client, "d2@x.com", 95, job_id="job-90-60")
    body = client.post(f"/api/test/{res['test_token']}/submit", json={"answers": answers(6)}).json()
    assert body["score"] == 60 and body["eligible_for_offer"] is True


# Test E: email failure is visible and does not corrupt data
def test_e_email_failure_is_logged_and_status_not_advanced(env):
    client, state, Session = env
    state["smtp_ok"] = False
    token = screen(client, "fail@x.com", 88)["test_token"]
    body = client.post(f"/api/test/{token}/submit", json={"answers": ALL_CORRECT}).json()

    assert body["status"] == "SELECTED"
    c = candidate(client, "fail@x.com")
    assert c["application_status"] == "SELECTED"
    assert c["test_score"] == 100 and c["test_status"] == "COMPLETED"
    assert "EMAIL_FAILED" in logs(Session, "fail@x.com")
    assert "EMAIL_SENT" not in logs(Session, "fail@x.com")
    assert client.post(f"/api/test/{token}/submit", json={"answers": ALL_CORRECT}).status_code == 400


def test_duplicate_screening_does_not_reset_candidate(env):
    client, _, _ = env
    first = screen(client, "dup@x.com", 80)
    client.post(f"/api/test/{first['test_token']}/submit", json={"answers": ALL_CORRECT})
    again = screen(client, "dup@x.com", 20)
    assert again["status"] == "DUPLICATE"
    c = candidate(client, "dup@x.com")
    assert c["application_status"] == "OFFER_SENT" and c["resume_score"] == 80
    assert len([x for x in client.get("/api/candidates").json() if x["email"] == "dup@x.com"]) == 1


def test_gemini_failure_does_not_reject_candidate(env, monkeypatch):
    client, state, _ = env
    import app.routes.candidates as cand
    from app.services.gemini_service import GeminiError

    def boom(**kw):
        raise GeminiError("Gemini API returned HTTP 503")

    monkeypatch.setattr(cand, "evaluate_resume_with_gemini", boom)
    r = client.post("/api/candidates/screen-resume", params={"name": "G", "email": "g@x.com", "job_id": "job-70-80"},
                    json="some resume")
    assert r.status_code == 502
    assert all(c["email"] != "g@x.com" for c in client.get("/api/candidates").json())


def test_screen_resume_endpoint_uses_gemini_score_against_job_threshold(env, monkeypatch):
    client, _, _ = env
    import app.routes.candidates as cand
    monkeypatch.setattr(cand, "evaluate_resume_with_gemini",
                        lambda **kw: {"eligible": False, "match_score": 72, "reason": "ok"})
    r = client.post("/api/candidates/screen-resume", params={"name": "H", "email": "h@x.com", "job_id": "job-70-80"},
                    json="python resume")
    assert r.status_code == 200 and r.json()["status"] == "SHORTLISTED"


def test_hr_can_view_resume(env):
    client, _, _ = env
    screen(client, "cv@x.com", 50, name="Cv Person")
    uuid = candidate(client, "cv@x.com")["candidate_id"]
    r = client.get(f"/api/candidates/{uuid}/resume").json()
    assert r["resume_text"] == "Resume of Cv Person" and r["resume_filename"] == "cv.pdf"
