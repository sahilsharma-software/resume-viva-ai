
from app.services.resume_parser import extract_text_from_pdf
from app.services.resume_analyzer import (
    extract_skills,
    detect_resume_sections,
)

pdf_path = "data/sample_resume.pdf"

text = extract_text_from_pdf(pdf_path)

skills = extract_skills(text)
sections = detect_resume_sections(text)

print("DETECTED SKILLS")
print("-" * 30)
for skill in skills:
    print(skill)
print("Total skills detected:", len(skills))

print("\nDETECTED RESUME SECTIONS")
print("-" * 30)
for section in sections:
    print(section)
print("Total sections detected:", len(sections))
