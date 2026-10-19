
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.resume_analyzer import analyze_resume
from app.services.resume_parser import extract_text_from_pdf

router = APIRouter()


class ResumeTextRequest(BaseModel):
    text: str


@router.post("/analyze")
def analyze_resume_text(request: ResumeTextRequest):
    result = analyze_resume(request.text)
    return result


@router.post("/upload")
def upload_resume(file: UploadFile = File(...)):
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

        return analyze_resume(extracted_text)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read the PDF file.",
        )
