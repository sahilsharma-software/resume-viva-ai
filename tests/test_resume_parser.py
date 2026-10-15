
from pathlib import Path

from app.services.resume_parser import extract_text_from_pdf

def test_extract_text_from_pdf():
    pdf_path = Path("data/sample_resume.pdf")

    extracted_text = extract_text_from_pdf(str(pdf_path))

    assert isinstance(extracted_text, str)
    assert len(extracted_text.strip()) > 0
