
import streamlit as st
import requests

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Resume AI | Dashboard",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://127.0.0.1:8000"

# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>
    /* Main application background */
    .stApp {
        background: #0b1120;
        color: #e5e7eb;
    }

    /* Main content spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263449;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] p {
        color: #e5e7eb;
    }

    /* Headings */
    h1, h2, h3 {
        color: #f8fafc !important;
    }

    /* Metric cards */
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

    /* Buttons */
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

    /* Content cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #2a3b55;
        border-radius: 14px;
        background: #111b2e;
    }

    /* Inputs */
    [data-baseweb="input"],
    [data-baseweb="select"],
    [data-baseweb="textarea"] {
        border-radius: 8px;
    }

    /* Dividers */
    hr {
        border-color: #263449;
    }

    /* Small helper text */
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

defaults = {
    "analysis_data": None,
    "mcq_data": [],
    "mcq_results": None,
    "viva_submitted": False,
}

for key, default_value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clear_mcq_answers():
    """Clear saved radio-button selections."""
    for index in range(len(st.session_state.mcq_data)):
        key = f"mcq_answer_{index}"
        if key in st.session_state:
            del st.session_state[key]


def call_backend_error(response, action):
    """Display a readable backend error."""
    st.error(
        f"{action} failed. "
        f"Status: {response.status_code}"
    )
    try:
        st.code(response.text)
    except Exception:
        st.write("The backend returned an unexpected error.")


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
        ],
        key="page_navigation",
    )

    st.divider()

    if st.session_state.analysis_data is not None:
        st.success("Resume analyzed")
        st.caption(
            f"Resume ID: "
            f"{st.session_state.analysis_data.get('resume_id', 'N/A')}"
        )
    else:
        st.info("No resume analyzed yet")

    st.divider()
    st.caption("Built with Streamlit + FastAPI")
    st.caption("Resume AI · Project Dashboard")

# =========================================================
# COMMON DATA
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
        'Welcome back! Manage your resume analysis, '
        'viva preparation and MCQ practice in one place.'
        '</p>',
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

        with c1:
            st.metric(
                "Resume ID",
                str(data.get("resume_id", "N/A")),
            )

        with c2:
            st.metric("Skills Detected", len(skills))

        with c3:
            st.metric("Viva Questions", len(viva_questions))

        with c4:
            if mcq_results is not None:
                st.metric(
                    "Latest MCQ Score",
                    f"{mcq_results.get('score_percentage', 0):.2f}%",
                )
            else:
                st.metric("Latest MCQ Score", "Not attempted")

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
                    "Practise technical questions extracted "
                    "from your resume analysis."
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
            st.subheader("📈 Latest MCQ Performance")

            score = mcq_results.get("score_percentage", 0)

            st.progress(
                max(0.0, min(1.0, score / 100)),
                text=f"Score: {score:.2f}%",
            )

            p1, p2, p3 = st.columns(3)

            p1.metric("Correct", mcq_results["correct_answers"])
            p2.metric("Incorrect", mcq_results["incorrect_answers"])
            p3.metric("Unanswered", mcq_results["unanswered"])

# =========================================================
# RESUME ANALYSIS PAGE
# =========================================================

elif page == "Resume Analysis":

    st.title("📄 Resume Analysis")
    st.markdown(
        '<p class="dashboard-subtitle">'
        'Upload a PDF resume to identify technical skills '
        'and prepare for interviews.'
        '</p>',
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
                    st.session_state.analysis_data = response.json()
                    st.session_state.mcq_data = []
                    st.session_state.mcq_results = None
                    st.session_state.viva_submitted = False

                    st.success("Resume analyzed successfully!")
                    st.rerun()

                else:
                    call_backend_error(response, "Resume analysis")

            except requests.RequestException as error:
                st.error(f"Could not connect to backend: {error}")

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
        'Practise technical questions based on your resume analysis.'
        '</p>',
        unsafe_allow_html=True,
    )

    data = st.session_state.analysis_data

    if data is None:
        st.warning(
            "Please analyze a resume first from the Resume Analysis page."
        )

    else:
        questions = data.get("viva_questions", [])

        if not questions:
            st.info("No viva questions are available.")
        else:
            st.write(f"**Total viva questions: {len(questions)}**")

            with st.form("viva_answers_form"):

                viva_answers = []

                for index, question in enumerate(questions, start=1):
                    with st.container(border=True):
                        st.markdown(f"**Q{index}. {question}**")

                        answer = st.text_area(
                            "Your answer",
                            key=(
                                f"viva_{data['resume_id']}_{index}"
                            ),
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
                    "Automatic viva answer evaluation is not "
                    "implemented yet."
                )

# =========================================================
# MCQ PRACTICE PAGE
# =========================================================

elif page == "MCQ Practice":

    st.title("📝 MCQ Practice")
    st.markdown(
        '<p class="dashboard-subtitle">'
        'Generate questions for supported skills, submit your answers '
        'and review your performance.'
        '</p>',
        unsafe_allow_html=True,
    )

    data = st.session_state.analysis_data

    if data is None:
        st.warning(
            "Please analyze a resume first from the Resume Analysis page."
        )

    else:
        skills = data.get("skills", [])

        if st.button("⚡ Generate MCQs", type="primary"):
            st.session_state.mcq_data = []
            st.session_state.mcq_results = None
            clear_mcq_answers()

            with st.spinner("Generating MCQs..."):

                for skill in skills:
                    try:
                        response = requests.post(
                            f"{API_URL}/mcqs",
                            json={"skill": skill},
                            timeout=30,
                        )

                        if response.status_code == 200:
                            result = response.json()

                            st.session_state.mcq_data.extend(
                                result.get("mcqs", [])
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

            if st.session_state.mcq_data:
                st.success("MCQs generated successfully!")
                st.rerun()
            else:
                st.warning(
                    "No MCQs are available for the supported "
                    "skills detected in this resume."
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

                        st.markdown(f"**{mcq['question']}**")

                        answer = st.radio(
                            "Select your answer",
                            mcq["options"],
                            index=None,
                            key=f"mcq_answer_{index}",
                        )

                        selected_answers.append(answer)

                submitted_mcqs = st.form_submit_button(
                    "✅ Submit MCQ Answers",
                    type="primary",
                )

            if submitted_mcqs:
                evaluation_answers = [
                    {
                        "skill": mcq["skill"],
                        "question": mcq["question"],
                        "answer": answer,
                    }
                    for mcq, answer in zip(mcqs, selected_answers)
                ]

                try:
                    with st.spinner("Evaluating your answers..."):
                        response = requests.post(
                            f"{API_URL}/mcqs/evaluate/combined",
                            json={"answers": evaluation_answers},
                            timeout=30,
                        )

                    if response.status_code == 200:
                        st.session_state.mcq_results = response.json()
                        st.success("Evaluation completed successfully!")
                    else:
                        call_backend_error(response, "MCQ evaluation")

                except requests.RequestException as error:
                    st.error(f"Could not connect to backend: {error}")

            # -------------------------
            # MCQ Results
            # -------------------------

            results = st.session_state.mcq_results

            if results is not None:
                st.divider()
                st.subheader("📊 Evaluation Results")

                r1, r2, r3, r4 = st.columns(4)

                r1.metric(
                    "Score",
                    f"{results['score_percentage']:.2f}%",
                )
                r2.metric(
                    "Correct",
                    results["correct_answers"],
                )
                r3.metric(
                    "Incorrect",
                    results["incorrect_answers"],
                )
                r4.metric(
                    "Unanswered",
                    results["unanswered"],
                )

                score = results["score_percentage"]

                st.progress(
                    max(0.0, min(1.0, score / 100)),
                    text=f"Your score: {score:.2f}%",
                )

                if score >= 80:
                    st.success(
                        "Excellent work! You achieved a strong score."
                    )
                elif score >= 50:
                    st.info(
                        "Good effort! Review your incorrect answers "
                        "to improve your score."
                    )
                else:
                    st.warning(
                        "Keep practising. Review the answers below "
                        "and try another attempt."
                    )

                st.subheader("📖 Question-wise Feedback")

                for index, feedback in enumerate(
                    results["question_feedback"],
                    start=1,
                ):
                    with st.container(border=True):
                        st.markdown(
                            f"**Q{index}. {feedback['question']}**"
                        )

                        status = feedback["status"]

                        if status == "correct":
                            st.success("Correct answer!")
                        elif status == "incorrect":
                            st.error("Incorrect answer.")
                        else:
                            st.warning("Not answered.")

                        st.write(
                            "Your answer: "
                            f"{feedback['selected_answer'] or 'Not answered'}"
                        )
                        st.write(
                            "Correct answer: "
                            f"{feedback['correct_answer']}"
                        )

                if st.button("🔄 Retry MCQs"):
                    st.session_state.mcq_results = None
                    clear_mcq_answers()
                    st.rerun()

# =========================================================
# FOOTER
# =========================================================

st.divider()
st.caption(
    "AI-Powered Resume Analysis & Viva Preparation System "
    "· Streamlit Frontend"
)
