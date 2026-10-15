from app.services.resume_parser import extract_text_from_pdf

pdf_path = "data/sample_resume.pdf"
text = extract_text_from_pdf(pdf_path)

print("RESUME TEXT EXTRACTION RESULT")
print("-" * 40)
print(text[:3000])
print("-" * 40)
print("Total characters extracted:", len(text))