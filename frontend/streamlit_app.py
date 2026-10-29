
import streamlit as st
import requests
import os

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Resume AI | Dashboard",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
REQUEST_TIMEOUT = 30

# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #0b1120;
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263449;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] p {
        color: #e5e7eb;
    }

    h1, h2, h3 {
        color: #f8fafc !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #17243a, #111b2e);
        border: 1px solid #2a3b55;
        border-radius: 14px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #a9b9d0 !important;
    }

    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 9px;
        border: 1px solid #3b82f6;
        background: #2563eb;
        color: white;
        font-weight: 600;
        min-height: 42px;
        transition: 0.2s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #1d4ed8;
        border-color: #60a5fa;
        color: white;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #2a3b55;
        border-radius: 14px;
        background: #111b2e;
    }

    [data-baseweb="input"],
    [data-baseweb="select"],
    [data-baseweb="textarea"] {
        border-radius: 8px;
    }

    hr {
        border-color: #263449;
    }

    .dashboard-subtitle {
        color: #9caec5;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .hero-card {
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #2a3b55;
        background: linear-gradient(120deg, #14233b, #101827);
        margin-bottom: 22px;
    }

    .hero-card p {
        color: #b9c8dc;
        margin-bottom: 0;
    }

    .skill-chip {
        background: #142b45;
        border: 1px solid #28527a;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        color: #bfdbfe;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "analysis_data": None,
    "mcq_data": [],
    "mcq_results": None,
    "viva_submitted": False,
    "ai_viva_questions": None,
    "ai_viva_resume_id": None,
}

for key, default_value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clear_mcq_answers():
    """Remove saved MCQ radio selections."""
    for key in list(st.session_state.keys()):
        if key.startswith("mcq_answer_"):
            del st.session_state[key]


def call_backend_error(response, action):
    """Show readable backend errors."""
    st.error(
        f"{action} failed. HTTP status: {response.status_code}"
    )

    try:
        detail = response.json()
    except ValueError:
        detail = response.text

    if detail:
        st.code(str(detail))


def fetch_mcq_history():
    """Fetch saved MCQ attempts."""
    try:
        response = requests.get(
            f"{API_URL}/mcq-attempts",
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            result = response.json()

            if isinstance(result, list):
                return result, None

            return [], "Unexpected history response format."

        return [], (
            f"History request failed with HTTP "
            f"{response.status_code}: {response.text}"
        )

    except requests.RequestException as error:
        return [], f"Could not connect to backend: {error}"


def safe_percentage(value):
    """Convert a score to a percentage between 0 and 100."""
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def clear_ai_viva():
    """Clear cached AI questions when the resume changes."""
    st.session_state.ai_viva_questions = None
    st.session_state.ai_viva_resume_id = None



def generate_ai_viva():
    """
    Generate AI viva questions for the selected resume.
    The backend database stores and reuses generated questions.
    """

    data = st.session_state.analysis_data

    if not isinstance(data, dict):
        st.warning("Please analyze a resume first.")
        return

    resume_id = data.get("resume_id")

    if resume_id is None:
        st.error(
            "Resume ID was not found. Please upload and analyze "
            "your resume again."
        )
        return

    # Reuse questions already loaded in this Streamlit session.
    if (
        st.session_state.ai_viva_questions
        and st.session_state.ai_viva_resume_id == resume_id
    ):
        st.info("Using the AI viva questions already loaded.")
        return

    try:
        with st.spinner("Loading AI viva questions..."):
            response = requests.post(
                f"{API_URL}/ai-viva",
                json={"resume_id": resume_id},
                timeout=90,
            )

        if response.status_code == 200:
            result = response.json()

            if not isinstance(result, dict):
                st.error("Unexpected AI viva response format.")
                return

            questions = result.get("ai_viva_questions", [])

            if (
                not isinstance(questions, list)
                or not questions
                or not all(
                    isinstance(question, str)
                    and question.strip()
                    for question in questions
                )
            ):
                st.error(
                    "The backend did not return valid AI viva questions."
                )
                return

            # Cache questions in Streamlit's current session.
            st.session_state.ai_viva_questions = questions
            st.session_state.ai_viva_resume_id = resume_id

            st.success(
                f"Loaded {len(questions)} AI viva questions!"
            )

        else:
            call_backend_error(response, "AI viva generation")

    except requests.Timeout:
        st.error(
            "The request timed out. Check the backend and try again."
        )

    except requests.RequestException as error:
        st.error(f"Could not connect to backend: {error}")

    except ValueError:
        st.error("The backend returned an invalid JSON response.")


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.title("📄 Resume AI")
    st.caption("Your personal interview preparation workspace")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Resume Analysis",
            "Viva Preparation",
            "MCQ Practice",
            "MCQ History",
        ],
        key="page_navigation",
    )

    st.divider()

    sidebar_data = st.session_state.analysis_data

    if sidebar_data is not None:
        st.success("Resume analyzed")
        st.caption(
            f"Resume ID: {sidebar_data.get('resume_id', 'N/A')}"
        )
    else:
        st.info("No resume analyzed yet")

    st.divider()
    st.caption("Built with Streamlit + FastAPI")
    st.caption("Resume AI · Project Dashboard")


# =========================================================
# COMMON SESSION DATA
# =========================================================

data = st.session_state.analysis_data
mcq_results = st.session_state.mcq_results


# =========================================================
# DASHBOARD PAGE
# =========================================================

if page == "Dashboard":
    st.title("📊 Dashboard")

    st.markdown(
        '<p class="dashboard-subtitle">'
        "Welcome back! Manage your resume analysis, "
        "viva preparation and MCQ practice in one place."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-card">
            <h2>AI-Powered Resume Assistant</h2>
            <p>
                Understand your technical skills, practise
                interview questions and track your MCQ performance.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history_data, history_error = fetch_mcq_history()

    if history_error:
        st.warning(
            "Saved MCQ analytics could not be loaded. "
            "Check that the FastAPI backend is running."
        )

    if data is None:
        st.info(
            "Your dashboard is ready. Open "
            "**Resume Analysis** from the sidebar to upload a PDF."
        )

        with st.container(border=True):
            st.subheader("🚀 Get Started")
            st.write(
                "1. Upload your resume in PDF format.\n\n"
                "2. Analyze your skills.\n\n"
                "3. Practise viva questions and MCQs."
            )

    else:
        skills = data.get("skills", [])
        viva_questions = data.get("viva_questions", [])

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Resume ID", str(data.get("resume_id", "N/A")))
        c2.metric("Skills Detected", len(skills))
        c3.metric("Viva Questions", len(viva_questions))

        if mcq_results is not None:
            latest_score = safe_percentage(
                mcq_results.get("score_percentage", 0)
            )
            c4.metric("Latest MCQ Score", f"{latest_score:.2f}%")
        else:
            c4.metric("Latest MCQ Score", "Not attempted")

        st.divider()
        st.subheader("💻 Detected Skills")

        if skills:
            skill_columns = st.columns(3)

            for index, skill in enumerate(skills):
                with skill_columns[index % 3]:
                    st.markdown(
                        f'<div class="skill-chip">✦ {skill}</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.warning("No skills were detected in the resume.")

    total_attempts = len(history_data)

    if history_data:
        scores = [
            safe_percentage(item.get("score_percentage", 0))
            for item in history_data
        ]
        average_score = sum(scores) / len(scores)
        latest_saved_score = scores[0]
    else:
        average_score = 0.0
        latest_saved_score = 0.0

    st.divider()
    st.subheader("📈 MCQ Performance Overview")

    a1, a2, a3 = st.columns(3)

    a1.metric("Total MCQ Attempts", total_attempts)
    a2.metric("Average MCQ Score", f"{average_score:.2f}%")

    if history_data:
        a3.metric("Latest Saved Score", f"{latest_saved_score:.2f}%")
    else:
        a3.metric("Latest Saved Score", "No attempts yet")

    if history_data:
        st.caption(
            "The latest saved score assumes the backend returns "
            "attempts in newest-first order."
        )

    st.divider()
    st.subheader("🎯 Your Preparation Workspace")

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.subheader("📄 Resume Analysis")
            st.write(
                "Review your uploaded resume and detected skills."
            )
            st.caption("Choose Resume Analysis in the sidebar.")

    with c2:
        with st.container(border=True):
            st.subheader("🎓 Viva Preparation")
            st.write(
                "Practise technical questions generated from your resume."
            )
            st.caption("Choose Viva Preparation in the sidebar.")

    with c3:
        with st.container(border=True):
            st.subheader("📝 MCQ Practice")
            st.write(
                "Attempt questions and review your score "
                "with answer-by-answer feedback."
            )
            st.caption("Choose MCQ Practice in the sidebar.")

    if mcq_results is not None:
        st.divider()
        st.subheader("📊 Latest MCQ Session")

        score = safe_percentage(
            mcq_results.get("score_percentage", 0)
        )

        st.progress(score / 100, text=f"Score: {score:.2f}%")

        p1, p2, p3 = st.columns(3)

        p1.metric("Correct", mcq_results.get("correct_answers", 0))
        p2.metric("Incorrect", mcq_results.get("incorrect_answers", 0))
        p3.metric("Unanswered", mcq_results.get("unanswered", 0))


# =========================================================
# RESUME ANALYSIS PAGE
# =========================================================

elif page == "Resume Analysis":
    st.title("📄 Resume Analysis")

    st.markdown(
        '<p class="dashboard-subtitle">'
        "Upload a PDF resume to identify technical skills "
        "and prepare for interviews."
        "</p>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose your resume (PDF)",
        type=["pdf"],
        key="resume_uploader",
    )

    if uploaded_file is not None:
        st.caption(f"Selected file: {uploaded_file.name}")

        if st.button("🔍 Analyze Resume", type="primary"):
            try:
                with st.spinner("Analyzing your resume..."):
                    response = requests.post(
                        f"{API_URL}/upload",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                "application/pdf",
                            )
                        },
                        timeout=60,
                    )

                if response.status_code == 200:
                    result = response.json()

                    if not isinstance(result, dict):
                        st.error(
                            "The backend returned an unexpected "
                            "resume analysis response."
                        )
                    else:
                        # Clear AI questions because this is a new analysis.
                        clear_ai_viva()

                        st.session_state.analysis_data = result
                        st.session_state.mcq_data = []
                        st.session_state.mcq_results = None
                        st.session_state.viva_submitted = False

                        clear_mcq_answers()

                        st.success("Resume analyzed successfully!")
                        st.rerun()

                else:
                    call_backend_error(response, "Resume analysis")

            except requests.RequestException as error:
                st.error(f"Could not connect to backend: {error}")

            except ValueError:
                st.error("The backend returned an invalid JSON response.")

    data = st.session_state.analysis_data

    if data is not None:
        st.divider()
        st.subheader("📋 Analysis Summary")

        c1, c2 = st.columns(2)

        c1.metric("Resume ID", str(data.get("resume_id", "N/A")))
        c2.metric("Skills Detected", len(data.get("skills", [])))

        st.subheader("💻 Skills Found")

        skills = data.get("skills", [])

        if skills:
            skill_columns = st.columns(3)

            for index, skill in enumerate(skills):
                with skill_columns[index % 3]:
                    with st.container(border=True):
                        st.markdown(f"### 💡 {skill}")
                        st.caption("Detected skill")
        else:
            st.info("No skills were detected.")

        with st.expander("View full analysis response"):
            st.json(data)


# =========================================================
# VIVA PREPARATION PAGE
# =========================================================

elif page == "Viva Preparation":
    st.title("🎓 Viva Preparation")

    st.markdown(
        '<p class="dashboard-subtitle">'
        "Practise rule-based and AI-generated technical questions."
        "</p>",
        unsafe_allow_html=True,
    )

    data = st.session_state.analysis_data

    if data is None:
        st.warning(
            "Please analyze a resume first from the Resume Analysis page."
        )

    else:
        resume_id = data.get("resume_id", "unknown")

        # -------------------------------------------------
        # RULE-BASED VIVA QUESTIONS
        # -------------------------------------------------

        st.subheader("📘 Standard Viva Questions")

        questions = data.get("viva_questions", [])

        if not questions:
            st.info("No standard viva questions are available.")
        else:
            st.write(f"**Total questions: {len(questions)}**")

            with st.form("viva_answers_form"):
                viva_answers = []

                for index, question in enumerate(questions, start=1):
                    with st.container(border=True):
                        st.markdown(f"**Q{index}. {question}**")

                        answer = st.text_area(
                            "Your answer",
                            key=f"viva_{resume_id}_{index}",
                        )
                        viva_answers.append(answer)

                submitted_viva = st.form_submit_button(
                    "Submit Viva Answers",
                    type="primary",
                )

            if submitted_viva:
                st.session_state.viva_submitted = True

                st.subheader("📝 Submitted Answers")

                for index, (question, answer) in enumerate(
                    zip(questions, viva_answers),
                    start=1,
                ):
                    with st.container(border=True):
                        st.markdown(f"**Q{index}. {question}**")

                        if answer.strip():
                            st.write(answer)
                        else:
                            st.caption("No answer provided.")

                st.info(
                    "Answers are displayed for review. "
                    "Automatic viva answer evaluation is not implemented yet."
                )

        # -------------------------------------------------
        # AI-GENERATED VIVA QUESTIONS
        # -------------------------------------------------

        st.divider()
        st.subheader("🤖 AI-Generated Viva Questions")

        st.write(
            "Generate personalized technical questions using Gemini. "
            "This makes an API request only when generation is needed."
        )

        cached_questions = st.session_state.ai_viva_questions
        cached_resume_id = st.session_state.ai_viva_resume_id

        has_cached_questions = (
            isinstance(cached_questions, list)
            and bool(cached_questions)
            and cached_resume_id == resume_id
        )

        if has_cached_questions:
            st.success(
                "AI questions are saved for this resume. "
                "Displaying them without another Gemini request."
            )

        if st.button(
            "🤖 Generate AI Viva Questions",
            type="primary",
            disabled=has_cached_questions,
            key="generate_ai_viva_button",
        ):
            generate_ai_viva()

        # Display cached questions below the button.
        cached_questions = st.session_state.ai_viva_questions

        if (
            isinstance(cached_questions, list)
            and cached_questions
            and st.session_state.ai_viva_resume_id == resume_id
        ):
            st.write(
                f"**Total AI questions: {len(cached_questions)}**"
            )

            for index, question in enumerate(
                cached_questions,
                start=1,
            ):
                with st.container(border=True):
                    st.markdown(f"**AI Q{index}. {question}**")

            st.caption(
                "These questions are stored in the current Streamlit "
                "session. Refreshing or restarting the session may clear them."
            )


# =========================================================
# MCQ PRACTICE PAGE
# =========================================================

elif page == "MCQ Practice":
    st.title("📝 MCQ Practice")

    st.markdown(
        '<p class="dashboard-subtitle">'
        "Generate questions for supported skills, submit your answers "
        "and review your performance."
        "</p>",
        unsafe_allow_html=True,
    )

    data = st.session_state.analysis_data

    if data is None:
        st.warning(
            "Please analyze a resume first from the Resume Analysis page."
        )

    else:
        skills = data.get("skills", [])

        if not skills:
            st.warning(
                "No skills were detected. Please check your resume analysis."
            )

        if st.button("⚡ Generate MCQs", type="primary"):
            st.session_state.mcq_data = []
            st.session_state.mcq_results = None
            clear_mcq_answers()

            if not skills:
                st.warning("There are no detected skills to practise.")
            else:
                with st.spinner("Generating MCQs..."):
                    for skill in skills:
                        try:
                            response = requests.post(
                                f"{API_URL}/mcqs",
                                json={"skill": skill},
                                timeout=REQUEST_TIMEOUT,
                            )

                            if response.status_code == 200:
                                result = response.json()

                                if isinstance(result, dict):
                                    generated = result.get("mcqs", [])

                                    if isinstance(generated, list):
                                        st.session_state.mcq_data.extend(
                                            generated
                                        )
                                    else:
                                        st.warning(
                                            f"Unexpected MCQ format for {skill}."
                                        )

                            elif response.status_code == 404:
                                continue

                            else:
                                st.warning(
                                    f"Could not fetch MCQs for {skill}: "
                                    f"{response.text}"
                                )

                        except requests.RequestException as error:
                            st.error(
                                f"Could not connect to backend: {error}"
                            )
                            break

                        except ValueError:
                            st.warning(
                                f"The backend returned invalid JSON for {skill}."
                            )

                if st.session_state.mcq_data:
                    st.success("MCQs generated successfully!")
                    st.rerun()
                else:
                    st.warning(
                        "No MCQs are available for the supported skills."
                    )

        mcqs = st.session_state.mcq_data

        if mcqs:
            st.divider()
            st.subheader("🧠 Answer the Questions")
            st.caption(f"Total questions: {len(mcqs)}")

            with st.form("mcq_form"):
                selected_answers = []

                for index, mcq in enumerate(mcqs):
                    with st.container(border=True):
                        st.caption(
                            f"QUESTION {index + 1}  •  "
                            f"{mcq.get('skill', 'General')}"
                        )

                        question_text = mcq.get("question", "")
                        options = mcq.get("options", [])

                        st.markdown(f"**{question_text}**")

                        if not isinstance(options, list) or not options:
                            st.warning(
                                "Options are unavailable for this question."
                            )
                            selected_answers.append(None)
                            continue

                        answer = st.radio(
                            "Select your answer",
                            options,
                            index=None,
                            key=f"mcq_answer_{index}",
                        )

                        selected_answers.append(answer)

                submitted_mcqs = st.form_submit_button(
                    "✅ Submit MCQ Answers",
                    type="primary",
                )

            if submitted_mcqs:
                evaluation_answers = []

                for mcq, answer in zip(mcqs, selected_answers):
                    evaluation_answers.append(
                        {
                            "skill": mcq.get("skill", "General"),
                            "question": mcq.get("question", ""),
                            "answer": answer,
                        }
                    )

                try:
                    with st.spinner("Evaluating your answers..."):
                        response = requests.post(
                            f"{API_URL}/mcqs/evaluate/combined",
                            json={"answers": evaluation_answers},
                            timeout=REQUEST_TIMEOUT,
                        )

                    if response.status_code == 200:
                        result = response.json()

                        if isinstance(result, dict):
                            st.session_state.mcq_results = result
                            st.success(
                                "Evaluation completed successfully!"
                            )
                        else:
                            st.error(
                                "Unexpected evaluation response."
                            )
                    else:
                        call_backend_error(response, "MCQ evaluation")

                except requests.RequestException as error:
                    st.error(f"Could not connect to backend: {error}")

                except ValueError:
                    st.error(
                        "The backend returned an invalid evaluation response."
                    )

            results = st.session_state.mcq_results

            if results is not None:
                st.divider()
                st.subheader("📊 Evaluation Results")

                score = safe_percentage(
                    results.get("score_percentage", 0)
                )

                r1, r2, r3, r4 = st.columns(4)

                r1.metric("Score", f"{score:.2f}%")
                r2.metric("Correct", results.get("correct_answers", 0))
                r3.metric("Incorrect", results.get("incorrect_answers", 0))
                r4.metric("Unanswered", results.get("unanswered", 0))

                st.progress(
                    score / 100,
                    text=f"Your score: {score:.2f}%",
                )

                if score >= 80:
                    st.success(
                        "Excellent work! You achieved a strong score."
                    )
                elif score >= 50:
                    st.info(
                        "Good effort! Review your incorrect answers."
                    )
                else:
                    st.warning(
                        "Keep practising and review the answers below."
                    )

                st.subheader("📖 Question-wise Feedback")

                feedback_items = results.get("question_feedback", [])

                if not feedback_items:
                    st.info("No question-wise feedback was returned.")
                else:
                    for index, feedback in enumerate(
                        feedback_items,
                        start=1,
                    ):
                        with st.container(border=True):
                            st.markdown(
                                f"**Q{index}. "
                                f"{feedback.get('question', 'Question')}**"
                            )

                            status = feedback.get("status", "unanswered")

                            if status == "correct":
                                st.success("Correct answer!")
                            elif status == "incorrect":
                                st.error("Incorrect answer.")
                            else:
                                st.warning("Not answered.")

                            selected_answer = feedback.get("selected_answer")
                            correct_answer = feedback.get(
                                "correct_answer",
                                "Not provided",
                            )

                            st.write(
                                "Your answer: "
                                f"{selected_answer or 'Not answered'}"
                            )
                            st.write(f"Correct answer: {correct_answer}")

                if st.button("🔄 Retry MCQs"):
                    st.session_state.mcq_results = None
                    clear_mcq_answers()
                    st.rerun()


# =========================================================
# MCQ PERFORMANCE HISTORY PAGE
# =========================================================

elif page == "MCQ History":
    st.title("📈 MCQ Performance History")

    st.markdown(
        '<p class="dashboard-subtitle">'
        "Review your previous MCQ attempts and track your progress."
        "</p>",
        unsafe_allow_html=True,
    )

    if st.button("🔄 Refresh History"):
        st.rerun()

    try:
        with st.spinner("Loading your MCQ history..."):
            response = requests.get(
                f"{API_URL}/mcq-attempts",
                timeout=REQUEST_TIMEOUT,
            )

        if response.status_code == 200:
            attempts = response.json()

            if not isinstance(attempts, list):
                st.error("The backend returned an unexpected history format.")

            elif not attempts:
                st.info(
                    "No MCQ attempts found yet. "
                    "Complete an MCQ practice session first."
                )

            else:
                scores = [
                    safe_percentage(
                        attempt.get("score_percentage", 0)
                    )
                    for attempt in attempts
                ]

                latest_score = scores[0]
                average_score = sum(scores) / len(scores)

                c1, c2, c3 = st.columns(3)

                c1.metric("Total Attempts", len(attempts))
                c2.metric("Latest Score", f"{latest_score:.2f}%")
                c3.metric("Average Score", f"{average_score:.2f}%")

                st.caption(
                    "Latest score assumes newest-first ordering."
                )

                st.divider()
                st.subheader("🕒 Previous Attempts")

                for attempt in attempts:
                    with st.container(border=True):
                        score = safe_percentage(
                            attempt.get("score_percentage", 0)
                        )

                        st.markdown(
                            f"### {attempt.get('skill', 'Unknown Skill')}"
                        )

                        st.progress(
                            score / 100,
                            text=f"Score: {score:.2f}%",
                        )

                        a1, a2, a3, a4 = st.columns(4)

                        a1.metric(
                            "Questions",
                            attempt.get("total_questions", 0),
                        )
                        a2.metric(
                            "Correct",
                            attempt.get("correct_answers", 0),
                        )
                        a3.metric(
                            "Incorrect",
                            attempt.get("incorrect_answers", 0),
                        )
                        a4.metric(
                            "Unanswered",
                            attempt.get("unanswered", 0),
                        )

                        created_at = attempt.get("created_at")

                        if created_at:
                            st.caption(f"Attempt date: {created_at}")

        else:
            call_backend_error(response, "Loading MCQ history")

    except requests.RequestException as error:
        st.error(f"Could not connect to backend: {error}")

    except ValueError:
        st.error("The backend returned an invalid history response.")


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI-Powered Resume Analysis & Viva Preparation System "
    "· Streamlit Frontend"
)
