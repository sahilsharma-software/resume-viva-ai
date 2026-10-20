
from fastapi import APIRouter, File, HTTPException, UploadFile,Depends
from pydantic import BaseModel

from app.services.resume_analyzer import analyze_resume
from app.services.viva_generator import generate_viva_questions
from app.services.resume_parser import extract_text_from_pdf

from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.resume import Resume

router = APIRouter()

class ResumeTextRequest(BaseModel):
    text: str

def add_viva_questions(result: dict) -> dict:
    result["viva_questions"] = generate_viva_questions(
        skills=result["skills"],
        section_content=result["section_content"],
    )
    return result

@router.post("/analyze")
def analyze_resume_text(request: ResumeTextRequest):
    result = analyze_resume(request.text)
    return add_viva_questions(result)


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
