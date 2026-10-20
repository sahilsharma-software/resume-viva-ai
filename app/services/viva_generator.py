
def generate_viva_questions(
    skills: list[str],
    section_content: dict[str, str],
) -> list[str]:
    """Generate basic viva questions from resume skills and projects."""

    questions = []

    skill_questions = {
        "Python": "What are the main features of Python?",
        "C++": "What is the difference between C and C++?",
        "Java": "What is the difference between JDK, JRE, and JVM?",
        "SQL": "What is the difference between a primary key and a foreign key?",
        "FastAPI": "What is FastAPI, and why did you choose it?",
        "Machine Learning": "What is the difference between supervised and unsupervised learning?",
        "NLP": "What is Natural Language Processing?",
        "PyTorch": "What is PyTorch used for?",
        "TensorFlow": "What is TensorFlow used for?",
        "LangChain": "What is LangChain, and how does it help build LLM applications?",
    }

    for skill in skills:
        question = skill_questions.get(skill)

        if question:
            questions.append(question)

    projects = section_content.get("Projects", "").strip()

    if projects:
        if "fp-growth" in projects.lower() or "fp growth" in projects.lower():
            questions.append(
                "Why did you choose FP-Growth for your project?"
            )
        if "fastapi" in projects.lower():
            questions.append(
                "How did you use FastAPI in your project?"
            )

        questions.append("Explain one project mentioned in your resume.")
        questions.append("What was your role and contribution to the project?")
        questions.append("What challenges did you face while building your project?")

    return list(dict.fromkeys(questions))