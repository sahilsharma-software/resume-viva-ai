
from app.services.resume_parser import extract_text_from_pdf
from app.services.resume_analyzer import (
    extract_skills,
    detect_resume_sections,
    extract_section_content,
)

pdf_path = "data/sample_resume.pdf"

text = extract_text_from_pdf(pdf_path)

skills = extract_skills(text)
sections = detect_resume_sections(text)
section_content = extract_section_content(text)

print("DETECTED SKILLS")
print("-" * 30)
for skill in skills:
    print(skill)

print("\nDETECTED RESUME SECTIONS")
print("-" * 30)
for section in sections:
    print(section)

print("\nEXTRACTED SECTION CONTENT")
print("-" * 30)
for section, content in section_content.items():
    print(f"\n{section}:")
    print(content)



sample_text = """Education
B.Tech Computer Science

Technical Skills
Python, FastAPI, SQL

Projects
AI Resume Analysis System
"""

print(extract_section_content(sample_text))
