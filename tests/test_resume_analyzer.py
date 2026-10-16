
from app.services.resume_analyzer import extract_skills,detect_resume_sections


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
