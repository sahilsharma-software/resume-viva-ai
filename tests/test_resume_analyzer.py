
from app.services.resume_analyzer import extract_skills


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
