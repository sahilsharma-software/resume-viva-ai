
from pathlib import Path


def test_analyze_resume_endpoint(client):
    response = client.post(
        "/analyze",
        json={
            "text": """
            Education
            B.Tech Computer Science

            Technical Skills
            Python, FastAPI, SQL

            Projects
            Resume Analysis System
            """
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert "Python" in result["skills"]
    assert "FastAPI" in result["skills"]
    assert "Education" in result["sections"]
    assert "Projects" in result["sections"]
    assert "viva_questions" in result
    assert len(result["viva_questions"]) > 0


def test_upload_resume_endpoint(client):
    pdf_path = Path("data/sample_resume.pdf")

    with pdf_path.open("rb") as pdf_file:
        response = client.post(
            "/upload",
            files={
                "file": (
                    "sample_resume.pdf",
                    pdf_file,
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert "skills" in result
    assert "sections" in result
    assert "Python" in result["skills"]
    assert "resume_id" in result
    assert isinstance(result["resume_id"], int)
    assert "viva_questions" in result
    assert len(result["viva_questions"]) > 0
