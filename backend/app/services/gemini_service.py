import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

def evaluate_resume_with_gemini(resume_text: str, job_description: str) -> dict:
    """
    Sends candidate resume text and job description to Google Gemini AI.
    Returns structured JSON analysis.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not configured in backend/.env")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    prompt = f"""You are an AI recruitment screening assistant.

Analyze the candidate resume against the provided job description.

Evaluate:
1. Required skills
2. Relevant experience
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

Job Description:
{job_description}

Candidate Resume:
{resume_text}"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        res_data = response.json()

        raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
        # Clean markdown codeblocks
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean_text)
        return parsed
    except Exception as e:
        logger.error(f"Gemini API Evaluation failed: {str(e)}")
        # Fallback evaluation if API error occurs
        return {
            "eligible": False,
            "match_score": 50,
            "skills_match": 50,
            "experience_match": 50,
            "education_match": 50,
            "relevance_score": 50,
            "matched_skills": [],
            "missing_skills": [],
            "reason": f"Evaluation error: {str(e)}"
        }
