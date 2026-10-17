
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
    """Detect recognized section headings in resume text."""

    known_sections = [
        "Education",
        "Experience",
        "Projects",
        "Technical Skills",
        "Certifications",
        "Achievements",
    ]

    found_sections = []

    for section in known_sections:
        pattern = r"(?<!\w)" + re.escape(section) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found_sections.append(section)

    return found_sections


def extract_section_content(text: str) -> dict[str, str]:
    """Extract content under recognized resume section headings."""

    section_aliases = {
        "Education": [
            "Education",
            "Academic Background",
        ],
        "Experience": [
            "Experience",
            "Work Experience",
            "Professional Experience",
        ],
        "Projects": [
            "Projects",
            "Personal Projects",
        ],
        "Technical Skills": [
            "Technical Skills",
            "Skills",
        ],
        "Certifications": [
            "Certifications",
            "Certificates",
            "Certificate",
        ],
        "Achievements": [
            "Achievements",
            "Achievement",
        ],
    }

    lines = text.splitlines()
    extracted_sections = {}
    current_section = None

    for line in lines:
        heading = line.strip().rstrip(":").strip()

        matched_section = None

        for standard_name, aliases in section_aliases.items():
            if any(
                heading.lower() == alias.lower()
                for alias in aliases
            ):
                matched_section = standard_name
                break

        if matched_section:
            current_section = matched_section
            extracted_sections.setdefault(current_section, [])
            continue

        if current_section and line.strip():
            extracted_sections[current_section].append(
                line.strip()
            )

    return {
        section: "\n".join(content)
        for section, content in extracted_sections.items()
    }


def analyze_resume(text: str) -> dict:
    """Analyze resume text and return structured results."""

    skills = extract_skills(text)
    sections = detect_resume_sections(text)
    section_content = extract_section_content(text)

    return {
        "skills": skills,
        "sections": sections,
        "section_content": section_content,
        "total_skills": len(skills),
    }
