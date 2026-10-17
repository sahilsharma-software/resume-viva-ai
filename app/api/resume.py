
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.resume_analyzer import analyze_resume

router = APIRouter()


class ResumeTextRequest(BaseModel):
    text: str


@router.post("/analyze")
def analyze_resume_text(request: ResumeTextRequest):
    result = analyze_resume(request.text)
    return result
