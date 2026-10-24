
from fastapi import APIRouter, File, HTTPException, UploadFile,Depends
from pydantic import BaseModel

from app.services.resume_analyzer import analyze_resume
from app.services.viva_generator import generate_viva_questions
from app.services.resume_parser import extract_text_from_pdf
from app.services.mcq_generator import generate_mcqs,evaluate_mcq_answers

from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.resume import Resume

router = APIRouter()

class ResumeTextRequest(BaseModel):
    text: str


class MCQRequest(BaseModel):
    skill: str


class MCQEvaluationRequest(BaseModel):
    skill: str
    answers: list[str]

class MCQAnswerItem(BaseModel):
    skill:str
    question:str
    answer:str | None = None

class CombinedMCQEvaluationRequest(BaseModel):
    answers: list[MCQAnswerItem]

def add_viva_questions(result: dict) -> dict:
    result["viva_questions"] = generate_viva_questions(
        skills=result["skills"],
        section_content=result["section_content"],
    )
    return result

@router.post("/mcqs")
def get_mcqs(request:MCQRequest):
    mcqs = generate_mcqs(request.skill)

    if not mcqs:
        raise HTTPException(
            status_code=404,
            detail="No MCQs available for this skill.",
        )
    public_mcqs = [
        {
            "question": mcq["question"],
            "options": mcq["options"],
            "skill": mcq["skill"],
        }
        for mcq in mcqs
    ]
    return {"mcqs": public_mcqs}


@router.post("/mcqs/evaluate")
def evaluate_mcqs(request: MCQEvaluationRequest):
    mcqs = generate_mcqs(request.skill)

    if not mcqs:
        raise HTTPException(
            status_code=404,
            detail="No MCQs available for this skill.",
        )

    try:
        result = evaluate_mcq_answers(
            mcqs=mcqs,
            answers=request.answers,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return result


@router.post("/mcqs/evaluate/combined")
def evaluate_combined_mcqs(
    request: CombinedMCQEvaluationRequest,
):
    if not request.answers:
        raise HTTPException(
            status_code=400,
            detail="At least one answer is required.",
        )

    mcqs_to_evaluate = []
    submitted_answers = []

    for item in request.answers:
        available_mcqs = generate_mcqs(item.skill)

        if not available_mcqs:
            raise HTTPException(
                status_code=404,
                detail=f"No MCQs available for skill: {item.skill}",
            )

        # Find the question in the trusted backend question bank
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

    try:
        result = evaluate_mcq_answers(
            mcqs=mcqs_to_evaluate,
            answers=submitted_answers,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return result



@router.post("/analyze")
def analyze_resume_text(request: ResumeTextRequest):
    result = analyze_resume(request.text)
    return add_viva_questions(result)


@router.post("/resume/mcqs")
def get_resume_mcqs(request: ResumeTextRequest):
    result = analyze_resume(request.text)

    resume_skills = result["skills"]
    all_mcqs = []

    for skill in resume_skills:
        mcqs = generate_mcqs(skill)

        for mcq in mcqs:
            all_mcqs.append({
                "question": mcq["question"],
                "options": mcq["options"],
                "skill": mcq["skill"],
            })

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



@router.post("/upload")
def upload_resume(file: UploadFile = File(...),db:Session=Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    try:
        import pymupdf

        with pymupdf.open(stream=file.file.read(), filetype="pdf") as pdf:
            extracted_text = "".join(page.get_text() for page in pdf)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF.",
            )
        resume = Resume(filename=file.filename,extracted_text = extracted_text)
        db.add(resume)
        db.commit()
        db.refresh(resume)
        result = analyze_resume(extracted_text)
        result["resume_id"] = resume.id

        return add_viva_questions(result)

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not process the PDF file or save the resume",
        )


@router.get("/resume/{resume_id}")
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(
        Resume.id == resume_id
    ).first()

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


@router.get("/resumes")
def get_all_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).order_by(
        Resume.created_at.desc()
    ).all()

    return [
        {
            "id": resume.id,
            "filename": resume.filename,
            "created_at": resume.created_at,
        }
        for resume in resumes
    ]
