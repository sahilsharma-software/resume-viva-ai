
from app.services.viva_generator import generate_viva_questions


def test_generates_questions_for_known_skills():
    questions = generate_viva_questions(
        skills=["Python", "FastAPI"],
        section_content={},
    )

    assert "What are the main features of Python?" in questions
    assert "What is FastAPI, and why did you choose it?" in questions
    assert len(questions) == 2


def test_generates_project_questions_when_projects_exist():
    questions = generate_viva_questions(
        skills=[],
        section_content={
            "Projects": "Resume Analysis System"
        },
    )

    assert len(questions) == 3
    assert "Explain one project mentioned in your resume." in questions


def test_returns_empty_list_for_empty_input():
    questions = generate_viva_questions(
        skills=[],
        section_content={},
    )

    assert questions == []


def test_ignores_unknown_skills():
    questions = generate_viva_questions(
        skills=["UnknownSkill"],
        section_content={},
    )

    assert questions == []


def test_does_not_generate_project_questions_for_empty_projects():
    questions = generate_viva_questions(
        skills=[],
        section_content={"Projects": "   "},
    )

    assert questions == []

def test_generates_fp_growth_question_for_matching_project():
    questions = generate_viva_questions(
        skills=[],
        section_content={
            "Projects": "Market Basket Analysis using FP-Growth"
        },
    )

    assert (
        "Why did you choose FP-Growth for your project?"
        in questions
    )

def test_generate_fastapi_question_for_matching_project():
    questions = generate_viva_questions(
    skills=[],
    section_content={
        "Projects": "Built a REST API using FastAPI"
    },
    )

    assert (
        "How did you use FastAPI in your project?"
        in questions
    )
def test_removes_duplicate_viva_questions():
    questions = generate_viva_questions(
        skills=["FastAPI", "FastAPI"],
        section_content={
            "Projects": "Built a project using FastAPI"
        },
    )

    assert len(questions) == len(set(questions))

def test_removes_duplicates_and_preserves_order():
    questions = [
        "What is Python?",
        "What is FastAPI?",
        "What is Python?",
        "What is SQL?",
    ]

    unique_questions = list(dict.fromkeys(questions))

    assert unique_questions == [
        "What is Python?",
        "What is FastAPI?",
        "What is SQL?",
    ]

def test_generator_returns_unique_questions_in_order():
    questions = generate_viva_questions(
        skills=["FastAPI", "Python"],
        section_content={
            "Projects": "Built a project using FastAPI"
        },
    )
    
    assert len(questions) == len(set(questions))
    assert questions[0] == "What is FastAPI, and why did you choose it?"
    assert questions[1] == "What are the main features of Python?"