
import pymupdf
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF resume."""

    extracted_text = ""

    with pymupdf.open(pdf_path) as pdf:
        for page in pdf:
            extracted_text += page.get_text()

    return extracted_text
