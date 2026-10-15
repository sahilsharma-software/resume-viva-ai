
import re


def extract_skills(text: str) -> list[str]:
    """Identify known technical skills in resume text."""

    known_skills = [
        "Python",
        "C++",
        "Java",
        "SQL",
        "FastAPI",
        "Machine Learning",
        "NLP",
        "PyTorch",
        "TensorFlow",
        "LangChain",
    ]

    found_skills = []

    for skill in known_skills:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills
