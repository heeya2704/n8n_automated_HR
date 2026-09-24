from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Candidate, TestResult, Job, WorkflowLog, TestStatus, ApplicationStatus
from app.schemas import TestVerifyResponse, TestSubmitRequest, TestSubmitResponse, QuestionItem
from app.services import trigger_n8n_test_result_webhook, generate_offer_letter_pdf

router = APIRouter(prefix="/api/test", tags=["Assessment Test"])

# Master Question Bank (Questions + Answer Key)
QUESTION_BANK = [
    {
        "id": 1,
        "category": "Pandas",
        "question": "Which library is commonly used for DataFrame operations in Python?",
        "options": ["NumPy", "Pandas", "Flask", "Requests"],
        "correct_answer": "Pandas"
    },
    {
        "id": 2,
        "category": "Python",
        "question": "Which decorator in Python is used to declare an asynchronous function?",
        "options": ["@asyncio.coroutine", "async def syntax", "@staticmethod", "@classmethod"],
        "correct_answer": "async def syntax"
    },
    {
        "id": 3,
        "category": "FastAPI",
        "question": "What is the primary library used by FastAPI for data validation and settings management?",
        "options": ["Marshmallow", "Pydantic", "SQLAlchemy", "WTForms"],
        "correct_answer": "Pydantic"
    },
    {
        "id": 4,
        "category": "Machine Learning",
        "question": "Which metric is best suited for evaluating an imbalanced classification problem?",
        "options": ["Accuracy", "F1-Score / ROC-AUC", "Mean Squared Error", "R-Squared"],
        "correct_answer": "F1-Score / ROC-AUC"
    },
    {
        "id": 5,
        "category": "SQL",
        "question": "Which SQL clause is used to filter records after aggregate function execution?",
        "options": ["WHERE", "GROUP BY", "HAVING", "ORDER BY"],
        "correct_answer": "HAVING"
    },
    {
        "id": 6,
        "category": "NumPy",
        "question": "What function in NumPy is used to create a 1D array with evenly spaced values within a given interval?",
        "options": ["np.arange", "np.reshape", "np.concat", "np.zeros"],
        "correct_answer": "np.arange"
    },
    {
        "id": 7,
        "category": "Basic Programming",
        "question": "What is the time complexity of looking up a key in a standard Python dictionary on average?",
        "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
        "correct_answer": "O(1)"
    },
    {
        "id": 8,
        "category": "Logical Reasoning",
        "question": "If a model has high bias and low variance, what problem is it experiencing?",
        "options": ["Overfitting", "Underfitting", "Optimal performance", "Data leakage"],
        "correct_answer": "Underfitting"
    },
    {
        "id": 9,
        "category": "Python",
        "question": "How do you achieve shallow copying of a dictionary 'd' in Python?",
        "options": ["d.copy()", "d.clone()", "copy(d)", "d.duplicate()"],
        "correct_answer": "d.copy()"
    },
    {
        "id": 10,
        "category": "SQL",
        "question": "Which JOIN returns all rows from the left table and matched rows from the right table?",
        "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"],
        "correct_answer": "LEFT JOIN"
    }
]

@router.get("/{token}", response_model=TestVerifyResponse)
def verify_test_token(token: str, db: Session = Depends(get_db)):
    """
    Validates a candidate test token.
    If valid and not submitted/expired, returns test metadata and questions.
    """
    candidate = db.query(Candidate).filter(Candidate.test_token == token).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Test link is invalid.")

    if candidate.test_status == TestStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Test link has already been used.")

    if candidate.test_token_expires_at and datetime.utcnow() > candidate.test_token_expires_at:
        candidate.test_status = TestStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=400, detail="Test link has expired.")

    # Mark test as IN_PROGRESS if not already
    if candidate.test_status == TestStatus.NOT_STARTED:
        candidate.test_status = TestStatus.IN_PROGRESS
        candidate.application_status = ApplicationStatus.TEST_STARTED
        db.commit()

    job = db.query(Job).filter(Job.id == candidate.job_id).first()
    job_title = job.title if job else "Python / Machine Learning Developer"

    # Sanitize questions (hide correct answers)
    sanitized_questions = [
        QuestionItem(
            id=q["id"],
            category=q["category"],
            question=q["question"],
            options=q["options"]
        )
        for q in QUESTION_BANK
    ]

    return TestVerifyResponse(
        valid=True,
        candidate_name=candidate.name,
        candidate_email=candidate.email,
        job_title=job_title,
        time_limit_minutes=30,
        total_questions=len(sanitized_questions),
        questions=sanitized_questions
    )

@router.post("/{token}/submit", response_model=TestSubmitResponse)
def submit_test(token: str, payload: TestSubmitRequest, db: Session = Depends(get_db)):
    """
    Submits candidate answers, calculates percentage score, updates database,
    and triggers n8n workflow for final decision (Offer vs Rejection).
    """
    candidate = db.query(Candidate).filter(Candidate.test_token == token).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Invalid token")

    if candidate.test_status == TestStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Test has already been submitted.")

    # Calculate score
    user_answers_map = {ans.question_id: ans.selected_option for ans in payload.answers}
    correct_count = 0
    total_q = len(QUESTION_BANK)

    for q in QUESTION_BANK:
        q_id = q["id"]
        selected = user_answers_map.get(q_id)
        if selected and selected.strip().lower() == q["correct_answer"].strip().lower():
            correct_count += 1

    percentage_score = int((correct_count / total_q) * 100) if total_q > 0 else 0

    # Get job passing score
    job = db.query(Job).filter(Job.id == candidate.job_id).first()
    passing_score = job.test_passing_score if job else 80

    # Update candidate record
    candidate.test_score = percentage_score
    candidate.test_status = TestStatus.COMPLETED
    candidate.application_status = ApplicationStatus.TEST_COMPLETED
    db.commit()

    # Save test result details
    test_result = TestResult(
        candidate_id=candidate.id,
        total_questions=total_q,
        correct_answers=correct_count,
        score=percentage_score,
        test_answers=user_answers_map
    )
    db.add(test_result)
    db.commit()

    is_passed = percentage_score >= passing_score

    # Determine final decision
    if is_passed:
        candidate.application_status = ApplicationStatus.SELECTED
        pdf_path = generate_offer_letter_pdf(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            job_title=job.title if job else "Python / Machine Learning Developer"
        )
        candidate.application_status = ApplicationStatus.OFFER_SENT
        db.commit()
    else:
        candidate.application_status = ApplicationStatus.TEST_FAILED
        db.commit()

    # Log workflow event
    log_status = "SELECTED" if is_passed else "TEST_FAILED"
    workflow_log = WorkflowLog(
        candidate_id=candidate.id,
        candidate_email=candidate.email,
        workflow_name="Test Result Evaluation",
        status=log_status,
        message=f"Candidate scored {percentage_score}% (Passing score: {passing_score}%).",
        test_score=percentage_score,
        application_status=candidate.application_status.value
    )
    db.add(workflow_log)
    db.commit()

    # Trigger n8n webhook asynchronously
    n8n_payload = {
        "candidate_id": str(candidate.id),
        "candidate_uuid": candidate.candidate_id,
        "candidate_name": candidate.name,
        "candidate_email": candidate.email,
        "job_id": candidate.job_id,
        "test_score": percentage_score,
        "passing_score": passing_score,
        "total_questions": total_q,
        "correct_answers": correct_count,
        "status": candidate.application_status.value,
        "eligible_for_offer": is_passed
    }
    trigger_n8n_test_result_webhook(n8n_payload)

    return TestSubmitResponse(
        message="Assessment test submitted successfully.",
        candidate_id=candidate.candidate_id,
        candidate_email=candidate.email,
        score=percentage_score,
        total_questions=total_q,
        correct_answers=correct_count,
        status=candidate.application_status.value,
        eligible_for_offer=is_passed
    )
