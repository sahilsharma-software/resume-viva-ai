
import re


def extract_skills(text: str) -> list[str]:
    """Identify and normalize known technical skills in resume text."""

    skill_aliases = {
        "Python": ["Python"],
        "C++": ["C++"],
        "Java": ["Java"],
        "SQL": ["SQL"],
        "FastAPI": ["FastAPI"],
        "Machine Learning": ["Machine Learning", "ML"],
        "NLP": ["NLP", "Natural Language Processing"],
        "PyTorch": ["PyTorch"],
        "TensorFlow": ["TensorFlow"],
        "LangChain": ["LangChain"],
    }

    found_skills = []

    for standard_skill, aliases in skill_aliases.items():
        for alias in aliases:
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"

            if re.search(pattern, text, re.IGNORECASE):
                found_skills.append(standard_skill)
                break

    return found_skills



def detect_resume_sections(text: str) -> list[str]:
    """Detect common section headings in resume text."""

    known_sections = [
        "Education",
        "Experience",
        "Projects",
        "Technical Skills",
        "Certifications",
    ]

    found_sections = []

    for section in known_sections:
        pattern = r"(?<!\w)" + re.escape(section) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found_sections.append(section)

    return found_sections
