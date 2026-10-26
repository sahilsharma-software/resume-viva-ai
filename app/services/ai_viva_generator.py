
import os

from dotenv import load_dotenv
from google import genai


def generate_ai_viva_questions(
    skills: list[str],
    section_content: dict[str, str],
) -> list[str]:

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(api_key=api_key)

    projects = section_content.get("Projects", "").strip()

    prompt = f"""
    You are a technical viva interviewer for a B.Tech CSE student.

    Generate exactly 5 technical viva questions based on the student's resume.

    Requirements:
    - Questions must be relevant to the student's skills and projects.
    - Prefer clear, specific technical questions.
    - Return exactly 5 questions, one per line.
    - Do not include answers.

    Skills:
    {skills}

    Project details:
    {projects}
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    response_text = (response.text or "").strip()

    if not response_text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    questions = []

    for line in response_text.splitlines():
        question = line.strip()

        question = question.lstrip("0123456789")
        question = question.lstrip(". )-").strip()

        if question:
            questions.append(question)

        if len(questions) == 5:
            break

    if not questions:
        raise RuntimeError(
            "Gemini did not return any viva questions."
        )

    return questions
