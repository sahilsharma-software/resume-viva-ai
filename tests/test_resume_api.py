
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


def test_generate_mcqs_endpoint(client):
    response = client.post(
        "/mcqs",
        json={"skill": "Python"},
    )

    assert response.status_code == 200

    result = response.json()

    assert "mcqs" in result
    assert len(result["mcqs"]) > 0
    assert "question" in result["mcqs"][0]
    assert "options" in result["mcqs"][0]
    assert "correct_answer" not in result["mcqs"][0]


def test_evaluate_mcqs_endpoint(client):
    response = client.post(
        "/mcqs/evaluate",
        json={
            "skill": "Python",
            "answers": ["def", "Dictionary"],
        },
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    assert response.status_code == 200


def test_evaluate_mcqs_wrong_number_of_answers(client):
    response = client.post(
        "/mcqs/evaluate",
        json={
            "skill": "Python",
            "answers": ["def"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Number of answers must match number of questions"
    )


def test_evaluate_mcqs_unsupported_skill(client):
    response = client.post(
        "/mcqs/evaluate",
        json={
            "skill": "Java",
            "answers": ["class", "object"],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "No MCQs available for this skill."
    )


def test_generate_mcqs_from_resume_endpoint(client):
    response = client.post(
        "/resume/mcqs",
        json={
            "text": """
            Technical Skills
            Python, FastAPI, SQL

            Projects
            Resume Analysis System
            """
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert "skills" in result
    assert "mcqs" in result
    assert "total_questions" in result

    assert "Python" in result["skills"]
    assert "FastAPI" in result["skills"]
    assert "SQL" in result["skills"]

    assert result["total_questions"] == len(result["mcqs"])
    assert result["total_questions"] > 0

    for mcq in result["mcqs"]:
        assert "question" in mcq
        assert "options" in mcq
        assert "skill" in mcq
        assert "correct_answer" not in mcq


def test_get_resume_endpoint(client):
    pdf_path = Path("data/sample_resume.pdf")

    with pdf_path.open("rb") as pdf_file:
        upload_response = client.post(
            "/upload",
            files={
                "file": (
                    "sample_resume.pdf",
                    pdf_file,
                    "application/pdf",
                )
            },
        )

    assert upload_response.status_code == 200

    resume_id = upload_response.json()["resume_id"]

    response = client.get(f"/resume/{resume_id}")

    assert response.status_code == 200

    result = response.json()

    assert result["id"] == resume_id
    assert result["filename"] == "sample_resume.pdf"
    assert "created_at" in result
    assert "extracted_text" not in result


def test_get_resume_not_found(client):
    response = client.get("/resume/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found."



def test_get_all_resumes_endpoint(client):
    pdf_path = Path("data/sample_resume.pdf")

    with pdf_path.open("rb") as pdf_file:
        upload_response = client.post(
            "/upload",
            files={
                "file": (
                    "sample_resume.pdf",
                    pdf_file,
                    "application/pdf",
                )
            },
        )

    assert upload_response.status_code == 200

    response = client.get("/resumes")

    assert response.status_code == 200

    result = response.json()

    assert isinstance(result, list)
    assert len(result) > 0

    for resume in result:
        assert "id" in resume
        assert "filename" in resume
        assert "created_at" in resume
        assert "extracted_text" not in resume


def test_get_all_resumes_returns_list(client):
    response = client.get("/resumes")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_evaluate_combined_mcqs_all_correct(client):
    response = client.post(
        "/mcqs/evaluate/combined",
        json={
            "answers": [
                {
                    "skill": "Python",
                    "question": (
                        "Which keyword defines a function in Python?"
                    ),
                    "answer": "def",
                },
                {
                    "skill": "SQL",
                    "question": (
                        "Which SQL command retrieves data from a table?"
                    ),
                    "answer": "SELECT",
                },
                {
                    "skill": "FastAPI",
                    "question": (
                        "Which Python framework is used to build APIs in this project?"
                    ),
                    "answer": "FastAPI",
                },
            ]
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total_questions"] == 3
    assert result["correct_answers"] == 3
    assert result["incorrect_answers"] == 0
    assert result["unanswered"] == 0
    assert result["score_percentage"] == 100.0
    assert len(result["question_feedback"]) == 3


def test_evaluate_combined_mcqs_incorrect_answers(client):
    response = client.post(
        "/mcqs/evaluate/combined",
        json={
            "answers": [
                {
                    "skill": "Python",
                    "question": (
                        "Which keyword defines a function in Python?"
                    ),
                    "answer": "function",
                },
                {
                    "skill": "SQL",
                    "question": (
                        "Which SQL command retrieves data from a table?"
                    ),
                    "answer": "SELECT",
                },
            ]
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total_questions"] == 2
    assert result["correct_answers"] == 1
    assert result["incorrect_answers"] == 1
    assert result["unanswered"] == 0
    assert result["score_percentage"] == 50.0


def test_evaluate_combined_mcqs_empty_answers(client):
    response = client.post(
        "/mcqs/evaluate/combined",
        json={"answers": []},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "At least one answer is required."
    )


def test_evaluate_combined_mcqs_unsupported_skill(client):
    response = client.post(
        "/mcqs/evaluate/combined",
        json={
            "answers": [
                {
                    "skill": "Java",
                    "question": "What is a class?",
                    "answer": "class",
                }
            ]
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "No MCQs available for skill: Java"
    )


def test_evaluate_combined_mcqs_invalid_question(client):
    response = client.post(
        "/mcqs/evaluate/combined",
        json={
            "answers": [
                {
                    "skill": "Python",
                    "question": "This question is not in the bank",
                    "answer": "def",
                }
            ]
        },
    )

    assert response.status_code == 400
    assert "Question does not belong" in (
        response.json()["detail"]
    )


def test_evaluate_combined_mcqs_unanswered(client):
    response = client.post(
        "/mcqs/evaluate/combined",
        json={
            "answers": [
                {
                    "skill": "Python",
                    "question": (
                        "Which keyword defines a function in Python?"
                    ),
                    "answer": None,
                }
            ]
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total_questions"] == 1
    assert result["correct_answers"] == 0
    assert result["incorrect_answers"] == 0
    assert result["unanswered"] == 1
    assert result["score_percentage"] == 0.0
    assert result["question_feedback"][0]["status"] == "unanswered"


