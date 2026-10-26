
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.resume import Resume
from app.models.mcq_attempt import MCQAttempt
from app.models.ai_viva_question import AIVivaQuestion

from app.services.resume_analyzer import analyze_resume
from app.services.viva_generator import generate_viva_questions
from app.services.mcq_generator import generate_mcqs, evaluate_mcq_answers

from app.services.ai_viva_generator import generate_ai_viva_questions


router = APIRouter()


# -------------------- Request Schemas --------------------

class ResumeTextRequest(BaseModel):
    text: str

class AIVivaRequest(BaseModel):
    resume_id: int


class MCQRequest(BaseModel):
    skill: str


class MCQEvaluationRequest(BaseModel):
    skill: str
    answers: list[str]


class MCQAnswerItem(BaseModel):
    skill: str
    question: str
    answer: str | None = None


class CombinedMCQEvaluationRequest(BaseModel):
    answers: list[MCQAnswerItem]


# -------------------- Viva Questions Helper --------------------

def add_viva_questions(result):
    skills = result.get("skills", [])
    section_content = result.get("section_content", {})

    result["viva_questions"] = generate_viva_questions(
        skills,
        section_content,
    )

    return result


# -------------------- Analyze Resume Text --------------------

@router.post("/analyze")
def analyze_resume_text(request: ResumeTextRequest):
    result = analyze_resume(request.text)
    return add_viva_questions(result)


# -------------------- Generate MCQs --------------------

@router.post("/mcqs")
def get_mcqs(request: MCQRequest):
    mcqs = generate_mcqs(request.skill)

    if not mcqs:
        raise HTTPException(
            status_code=404,
            detail="No MCQs available for this skill.",
        )

    # Never expose correct answers before evaluation.
    public_mcqs = [
        {
            "question": mcq["question"],
            "options": mcq["options"],
            "skill": mcq["skill"],
        }
        for mcq in mcqs
    ]

    return {
        "mcqs": public_mcqs,
        "total_questions": len(public_mcqs),
    }


# -------------------- Evaluate MCQs for One Skill --------------------

@router.post("/mcqs/evaluate")
def evaluate_mcqs(request: MCQEvaluationRequest):
    mcqs = generate_mcqs(request.skill)

    if not mcqs:
        raise HTTPException(
            status_code=404,
            detail="No MCQs available for this skill.",
        )

    try:
        return evaluate_mcq_answers(
            mcqs=mcqs,
            answers=request.answers,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# -------------------- Evaluate Combined MCQs and Save Attempts --------------------

@router.post("/mcqs/evaluate/combined")
def evaluate_combined_mcqs(
    request: CombinedMCQEvaluationRequest,
    db: Session = Depends(get_db),
):
    if not request.answers:
        raise HTTPException(
            status_code=400,
            detail="At least one answer is required.",
        )

    mcqs_to_evaluate = []
    submitted_answers = []
    skill_groups = {}

    # Validate submitted questions against the backend question bank.
    for item in request.answers:
        available_mcqs = generate_mcqs(item.skill)

        if not available_mcqs:
            raise HTTPException(
                status_code=404,
                detail=f"No MCQs available for skill: {item.skill}",
            )

        matched_mcq = next(
            (
                mcq
                for mcq in available_mcqs
                if mcq["question"].strip() == item.question.strip()
            ),
            None,
        )

        if matched_mcq is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Question does not belong to the "
                    f"question bank for skill: {item.skill}"
                ),
            )

        mcqs_to_evaluate.append(matched_mcq)
        submitted_answers.append(item.answer or "")

        skill_groups.setdefault(
            item.skill,
            {"mcqs": [], "answers": []},
        )

        skill_groups[item.skill]["mcqs"].append(matched_mcq)
        skill_groups[item.skill]["answers"].append(item.answer or "")

    try:
        # Calculate the overall quiz result.
        result = evaluate_mcq_answers(
            mcqs=mcqs_to_evaluate,
            answers=submitted_answers,
        )

        # Save one performance record for each skill.
        for skill, group in skill_groups.items():
            skill_result = evaluate_mcq_answers(
                mcqs=group["mcqs"],
                answers=group["answers"],
            )

            attempt = MCQAttempt(
                skill=skill,
                total_questions=skill_result["total_questions"],
                correct_answers=skill_result["correct_answers"],
                incorrect_answers=skill_result["incorrect_answers"],
                unanswered=skill_result["unanswered"],
                score_percentage=skill_result["score_percentage"],
            )

            db.add(attempt)

        # Save all skill attempts in one transaction.
        db.commit()

        return result

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not evaluate or save MCQ performance.",
        ) from exc


# -------------------- Generate MCQs from Resume Text --------------------

@router.post("/resume/mcqs")
def get_resume_mcqs(request: ResumeTextRequest):
    result = analyze_resume(request.text)
    resume_skills = result.get("skills", [])

    all_mcqs = []

    for skill in resume_skills:
        mcqs = generate_mcqs(skill)

        for mcq in mcqs:
            all_mcqs.append(
                {
                    "question": mcq["question"],
                    "options": mcq["options"],
                    "skill": mcq["skill"],
                }
            )

    if not all_mcqs:
        raise HTTPException(
            status_code=404,
            detail="No MCQs available for the skills found in this resume.",
        )

    return {
        "skills": resume_skills,
        "mcqs": all_mcqs,
        "total_questions": len(all_mcqs),
    }


# -------------------- Upload Resume PDF --------------------


@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    try:
        import pymupdf

        with pymupdf.open(
            stream=file.file.read(),
            filetype="pdf",
        ) as pdf:
            extracted_text = "".join(
                page.get_text() for page in pdf
            )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF.",
            )

        resume = Resume(
            filename=file.filename,
            extracted_text=extracted_text,
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        result = analyze_resume(extracted_text)
        result["resume_id"] = resume.id
        result["extracted_text"] = extracted_text

        return add_viva_questions(result)

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not process the PDF file or save the resume.",
        ) from exc

# -------------------- Get Resume by ID --------------------

@router.get("/resume/{resume_id}")
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id)
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    return {
        "id": resume.id,
        "filename": resume.filename,
        "created_at": resume.created_at,
    }

# -------------------- Get All Saved Resumes --------------------

@router.get("/resumes")
def get_resumes(db: Session = Depends(get_db)):
    resumes = (
        db.query(Resume)
        .order_by(Resume.id.desc())
        .all()
    )

    return [
        {
            "id": resume.id,
            "filename": resume.filename,
            "created_at": resume.created_at,
        }
        for resume in resumes
    ]
@router.get("/mcq-attempts")
def get_mcq_attempts(
    db: Session = Depends(get_db),
):
    attempts = (
        db.query(MCQAttempt)
        .order_by(MCQAttempt.created_at.desc())
        .all()
    )

    return [
        {
            "id": attempt.id,
            "skill": attempt.skill,
            "total_questions": attempt.total_questions,
            "correct_answers": attempt.correct_answers,
            "incorrect_answers": attempt.incorrect_answers,
            "unanswered": attempt.unanswered,
            "score_percentage": attempt.score_percentage,
            "created_at": attempt.created_at,
        }
        for attempt in attempts
    ]

# -------------------- Generate AI Viva Questions --------------------
@router.post("/ai-viva")
def generate_ai_viva(
    request: AIVivaRequest,
    db: Session = Depends(get_db),
):
    # Step 1: Fetch resume from database
    resume = (
        db.query(Resume)
        .filter(Resume.id == request.resume_id)
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    # Step 2: Analyze the saved resume text
    result = analyze_resume(resume.extracted_text or "")

    skills = result.get("skills", [])
    section_content = result.get("section_content", {})

    # Step 3: Check for previously saved AI questions
    saved_questions = (
        db.query(AIVivaQuestion)
        .filter(AIVivaQuestion.resume_id == resume.id)
        .all()
    )

    if saved_questions:
        return {
            "resume_id": resume.id,
            "skills": skills,
            "ai_viva_questions": [
                item.question for item in saved_questions
            ],
        }

    # Step 4: Generate new questions using Gemini
    try:
        questions = generate_ai_viva_questions(
            skills,
            section_content,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    # Step 5: Save generated questions in the database
    try:
        for question in questions:
            db.add(
                AIVivaQuestion(
                    resume_id=resume.id,
                    question=question,
                )
            )

        db.commit()

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save AI viva questions.",
        ) from exc

    # Step 6: Return the response
    return {
        "resume_id": resume.id,
        "skills": skills,
        "ai_viva_questions": questions,
    }