
import streamlit as st
import requests

st.title("AI-Powered Resume Analysis")

st.subheader("Resume Analysis & Viva Preparation System")

st.write(
    "Upload your resume to analyze your skills "
    "and prepare for technical viva questions."
)

# Store analysis results between reruns
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

uploaded_file = st.file_uploader(
    label="Upload your resume (PDF)",
    type=["pdf"]
)

if uploaded_file:
    st.write("Uploaded file:", uploaded_file.name)

    if st.button("Analyze Resume"):
        try:
            with st.spinner("Analyzing resume..."):
                response = requests.post(
                    "http://127.0.0.1:8000/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    },
                    timeout=60
                )

            if response.status_code == 200:
                st.session_state.analysis_data = response.json()
                st.success("Resume analyzed successfully!")
            else:
                st.error(
                    f"Error: {response.status_code} - "
                    f"{response.text}"
                )

        except requests.RequestException as error:
            st.error(f"Could not connect to backend: {error}")

# Display saved analysis after every rerun
data = st.session_state.analysis_data

if data is not None:
    st.write("Resume ID:", data["resume_id"])

    st.subheader("Skills Found")

    for skill in data["skills"]:
        st.success(skill)

    st.subheader("Technical Viva Questions")

    # Keep all answer inputs inside one form
    with st.form("viva_answers_form"):
        for index, question in enumerate(
            data["viva_questions"], start=1
        ):
            st.write(f"**Q{index}.** {question}")

            st.text_area(
                "Your Answer",
                key=f"answer_{data['resume_id']}_{index}"
            )

        submitted = st.form_submit_button("Submit Answers")

    if submitted:
        st.subheader("Your Submitted Answers")

        for index, question in enumerate(
            data["viva_questions"], start=1
        ):
            answer_key = f"answer_{data['resume_id']}_{index}"
            answer = st.session_state.get(answer_key, "")

            st.write(f"**Q{index}.** {question}")

            if answer.strip():
                st.write(f"**Your Answer:** {answer}")
            else:
                st.write("No answer provided.")
