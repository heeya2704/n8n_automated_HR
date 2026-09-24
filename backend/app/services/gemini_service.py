import os
import json
import time
import requests
import logging

logger = logging.getLogger(__name__)


class GeminiError(Exception):
    pass


def evaluate_resume_with_gemini(resume_text: str, job) -> dict:
    """
    Sends candidate resume text and the job requirements to Google Gemini AI.
    Returns structured JSON analysis. Raises GeminiError on any failure so callers
    never treat an API outage as a real (rejecting) score.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise GeminiError("GEMINI_API_KEY is not configured in backend/.env")

    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    skills = ", ".join(job.required_skills or [])
    prompt = f"""You are an AI recruitment screening assistant.

Analyze the candidate resume against the provided job description.

Evaluate:
1. Required skills ({skills})
2. Relevant experience (required: {job.minimum_experience})
3. Education
4. Projects
5. Technologies
6. Overall job relevance

Do not make decisions based on protected or sensitive personal characteristics.

Return ONLY valid JSON matching this schema:
{{
  "eligible": true/false,
  "match_score": 0-100,
  "skills_match": 0-100,
  "experience_match": 0-100,
  "education_match": 0-100,
  "relevance_score": 0-100,
  "matched_skills": [],
  "missing_skills": [],
  "reason": ""
}}

Job Title: {job.title}

Job Description:
{job.description}

Candidate Resume:
{resume_text}"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }

    try:
        for attempt in range(3):
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                timeout=60,
            )
            if response.status_code not in (429, 503) or attempt == 2:
                break
            time.sleep(2 ** (attempt + 1))
        response.raise_for_status()
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean_text)
        parsed["match_score"] = int(parsed.get("match_score", 0))
        return parsed
    except requests.HTTPError as e:
        logger.error(f"Gemini API HTTP error: {e.response.status_code} {e.response.text[:300]}")
        raise GeminiError(f"Gemini API returned HTTP {e.response.status_code}") from e
    except Exception as e:
        logger.error(f"Gemini API evaluation failed: {e}")
        raise GeminiError(f"Gemini evaluation failed: {e}") from e
