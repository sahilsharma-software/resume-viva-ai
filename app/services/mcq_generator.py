def generate_mcqs(skill: str) -> list[dict]:
    """Generate MCQs for a given technical skill."""

    question_bank = {
        "Python": [
            {
                "question": "Which keyword defines a function in Python?",
                "options": ["func", "def", "function", "define"],
                "correct_answer": "def",
                "skill": "Python",
            },
            {
                "question": "Which data type stores key-value pairs?",
                "options": ["List", "Tuple", "Dictionary", "Set"],
                "correct_answer": "Dictionary",
                "skill": "Python",
            },
        ],
        "FastAPI": [
            {
                "question": "Which Python framework is used to build APIs in this project?",
                "options": ["Django", "FastAPI", "Flask", "Pandas"],
                "correct_answer": "FastAPI",
                "skill": "FastAPI",
            },
            {
                "question": "Which HTTP method is commonly used to submit data to an API?",
                "options": ["GET", "POST", "HEAD", "OPTIONS"],
                "correct_answer": "POST",
                "skill": "FastAPI",
            },
        ],
        "SQL": [
            {
                "question": "Which SQL command retrieves data from a table?",
                "options": ["GET", "FETCH", "SELECT", "OPEN"],
                "correct_answer": "SELECT",
                "skill": "SQL",
            },
            {
                "question": "Which SQL clause filters rows based on a condition?",
                "options": ["ORDER BY", "WHERE", "GROUP BY", "JOIN"],
                "correct_answer": "WHERE",
                "skill": "SQL",
            },
        ],
    }

    normalized_skill = skill.strip().casefold()

    for known_skill, mcqs in question_bank.items():
        if known_skill.casefold() == normalized_skill:
            return mcqs

    return []


def evaluate_mcq_answers(
    mcqs: list[dict],
    answers: list[str],
) -> dict:
    """Evaluate MCQ answers and provide question-wise feedback."""

    if len(answers) != len(mcqs):
        raise ValueError(
            "Number of answers must match number of questions"
        )

    total_questions = len(mcqs)
    correct_answers = 0
    unanswered = 0
    question_feedback = []

    for mcq, answer in zip(mcqs, answers):
        correct_answer = mcq["correct_answer"]
        selected_answer = (answer or "").strip()

        if not selected_answer:
            unanswered += 1
            status = "unanswered"

        elif (
            selected_answer.casefold()
            == correct_answer.strip().casefold()
        ):
            correct_answers += 1
            status = "correct"

        else:
            status = "incorrect"

        question_feedback.append({
            "question": mcq.get("question", ""),
            "selected_answer": selected_answer,
            "correct_answer": correct_answer,
            "status": status,
        })

    incorrect_answers = (
        total_questions - correct_answers - unanswered
    )

    if total_questions > 0:
        score_percentage = (
            correct_answers / total_questions
        ) * 100
    else:
        score_percentage = 0.0

    return {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "incorrect_answers": incorrect_answers,
        "unanswered": unanswered,
        "score_percentage": round(score_percentage, 2),
        "question_feedback": question_feedback,
    }
