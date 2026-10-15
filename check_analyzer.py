from app.services.resume_analyzer import extract_skills 
from app.services.resume_parser import extract_text_from_pdf

pdf_path ="data/sample_resume.pdf"

text = extract_text_from_pdf(pdf_path)
skills = extract_skills(text)


print("DETECTED SKILLS")
print("-" * 30)

for skill in skills:
    print(skill)

print("-" * 30)
print("Total skills detected:", len(skills))