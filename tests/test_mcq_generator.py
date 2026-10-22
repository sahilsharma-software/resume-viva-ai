from app.services.mcq_generator import generate_mcqs,evaluate_mcq_answers
import pytest


def test_generate_mcqs_for_python():
    mcqs = generate_mcqs("Python")

    assert len(mcqs) == 2
    assert mcqs[0]["question"] == "Which keyword defines a function in Python?"
    assert mcqs[0]["correct_answer"] == "def"


def test_generate_mcqs_for_unknown_skill():
    mcqs = generate_mcqs("Rust")

    assert mcqs == []

def test_evaluate_all_correct_answers():
    mcqs = [
        {"correct_answer": "def"},
        {"correct_answer": "Dictionary"},
    ]
    answers = ["def", "Dictionary"]

    result = evaluate_mcq_answers(mcqs, answers)

    assert result["total_questions"] == 2
    assert result["correct_answers"] == 2
    assert result["incorrect_answers"] == 0
    assert result["unanswered"] == 0
    assert result["score_percentage"] == 100.0

def test_evaluate_mixed_answers():
    mcqs = [
        {"correct_answer": "def"},
        {"correct_answer": "Dictionary"},
    ]
    answers = ["def", "List"]

    result = evaluate_mcq_answers(mcqs, answers)

    assert result["correct_answers"] == 1
    assert result["incorrect_answers"] == 1
    assert result["unanswered"] == 0
    assert result["score_percentage"] == 50.0


def test_evaluate_unanswered_questions():
    mcqs = [
        {"correct_answer": "def"},
        {"correct_answer": "Dictionary"},
    ]
    answers = ["def", ""]

    result = evaluate_mcq_answers(mcqs, answers)

    assert result["correct_answers"] == 1
    assert result["incorrect_answers"] == 0
    assert result["unanswered"] == 1
    assert result["score_percentage"] == 50.0

def test_evaluate_rejects_mismatched_answer_count():
    mcqs = [
        {"correct_answer": "def"},
        {"correct_answer": "Dictionary"},
    ]
    answers = ["def"]

    with pytest.raises(ValueError):
        evaluate_mcq_answers(mcqs, answers)

def test_evaluate_empty_question_list():
    result = evaluate_mcq_answers([], [])

    assert result["total_questions"] == 0
    assert result["score_percentage"] == 0.0


def test_evaluate_case_insensitive_answers():
    mcqs = [{"correct_answer": "Dictionary"}]
    answers = ["dictionary"]

    result = evaluate_mcq_answers(mcqs, answers)

    assert result["correct_answers"] == 1
    assert result["score_percentage"] == 100.0


def test_generate_fastapi_mcqs():
    from app.services.mcq_generator import generate_mcqs

    mcqs = generate_mcqs("FastAPI")

    assert len(mcqs) == 2
    assert all(mcq["skill"] == "FastAPI" for mcq in mcqs)


def test_generate_sql_mcqs():
    from app.services.mcq_generator import generate_mcqs

    mcqs = generate_mcqs("SQL")

    assert len(mcqs) == 2
    assert all(mcq["skill"] == "SQL" for mcq in mcqs)


def test_generate_mcqs_ignores_case_and_whitespace():
    from app.services.mcq_generator import generate_mcqs

    assert generate_mcqs(" python ") == generate_mcqs("Python")


def test_evaluate_returns_question_wise_feedback():
    mcqs = [
        {
            "question": "Which keyword defines a function?",
            "correct_answer": "def",
        },
        {
            "question": "Which data type stores key-value pairs?",
            "correct_answer": "Dictionary",
        },
    ]

    answers = ["def", "List"]

    result = evaluate_mcq_answers(mcqs, answers)

    assert len(result["question_feedback"]) == 2

    assert result["question_feedback"][0]["status"] == "correct"
    assert result["question_feedback"][1]["status"] == "incorrect"

    assert result["question_feedback"][0]["correct_answer"] == "def"
    assert result["question_feedback"][1]["correct_answer"] == "Dictionary"


def test_evaluate_feedback_for_unanswered_question():
    mcqs = [
        {
            "question": "Which keyword defines a function?",
            "correct_answer": "def",
        },
    ]

    result = evaluate_mcq_answers(mcqs, [""])

    assert result["unanswered"] == 1
    assert result["question_feedback"][0]["status"] == "unanswered"
    assert result["question_feedback"][0]["selected_answer"] == ""
    assert result["question_feedback"][0]["correct_answer"] == "def"


def test_evaluate_all_answers_blank():
    mcqs = [
        {
            "question": "Which keyword defines a function?",
            "correct_answer": "def",
        },
        {
            "question": "Which data type stores key-value pairs?",
            "correct_answer": "Dictionary",
        },
    ]

    result = evaluate_mcq_answers(mcqs, ["", ""])

    assert result["total_questions"] == 2
    assert result["correct_answers"] == 0
    assert result["incorrect_answers"] == 0
    assert result["unanswered"] == 2
    assert result["score_percentage"] == 0.0

    assert result["question_feedback"][0]["status"] == "unanswered"
    assert result["question_feedback"][1]["status"] == "unanswered"
