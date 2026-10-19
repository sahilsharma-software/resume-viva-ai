
from app.services.resume_analyzer import extract_skills,detect_resume_sections,extract_section_content,analyze_resume


def test_extract_skills():
    text = "Technical Skills: Python, SQL, FastAPI"

    skills = extract_skills(text)

    assert "Python" in skills
    assert "SQL" in skills
    assert "FastAPI" in skills

def test_sql_does_not_match_sqlalchemy():
    text = "Experience with SQLAlchemy"

    skills = extract_skills(text)

    assert "SQL" not in skills

def test_detect_resume_sections():
    text = """
    EDUCATION,
    Technical Skills,
    Projects
    """

    sections = detect_resume_sections(text)

    assert "Education" in sections
    assert "Technical Skills" in sections
    assert "Projects" in sections
    assert "Experience" not in sections


def test_detect_singular_certification_section():
    text = """
    Education
    CERTIFICATION
    Artificial Intelligence using Python
    Projects
    """

    sections = detect_resume_sections(text)

    assert "Education" in sections
    assert "Certifications" in sections
    assert "Projects" in sections




def test_extract_section_content_keeps_sections_separate():
    text = """
    Education
    B.Tech in Computer Science

    Projects
    Resume Analysis System

    Achievements
    Solved 300+ coding problems

    Certificate
    Completed AI training
    """

    sections = extract_section_content(text)

    assert "B.Tech in Computer Science" in sections["Education"]
    assert "Resume Analysis System" in sections["Projects"]
    assert "Solved 300+ coding problems" in sections["Achievements"]
    assert "Completed AI training" in sections["Certifications"]

    assert "Solved 300+ coding problems" not in sections["Projects"]


def test_extract_skills_from_empty_text():
    skills = extract_skills("")

    assert skills == []

def test_extract_skills_when_no_known_skill_exist():
    text = "i love to play cricket and badminton"
    skills = extract_skills(text)

    assert skills ==[]

def test_extract_skills_with_no_duplicate():
    text=" i am having python learing and experience with python"

    skills = extract_skills(text)
    assert skills.count("Python") == 1


def test_extract_skills_handles_mixed_case():
    text = "I use python, FASTAPI, and machine learning."

    skills = extract_skills(text)

    assert "Python" in skills
    assert "FastAPI" in skills
    assert "Machine Learning" in skills


def test_analyze_resume():
    text = """
    Education
    B.Tech Computer Science

    Technical Skills
    Python, FastAPI, SQL

    Projects
    Resume Analysis System
    """

    result = analyze_resume(text)

    assert isinstance(result, dict)
    assert "Python" in result["skills"]
    assert "FastAPI" in result["skills"]
    assert "Education" in result["sections"]
    assert result["total_skills"] == len(result["skills"])
    assert "Education" in result["section_content"]

    
    
def test_analyze_resume_with_empty_text():
    result = analyze_resume("")

    assert result["skills"] == []
    assert result["sections"] == []
    assert result["section_content"] == {}
    assert result["total_skills"] == 0

