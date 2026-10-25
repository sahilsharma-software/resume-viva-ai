# AI-Powered Resume Analysis and Viva Preparation System

## 1. Project Overview

The AI-Powered Resume Analysis and Viva Preparation System is a web-based application designed to analyze resumes and help students prepare for technical interviews and viva examinations.

The system extracts information from PDF resumes, identifies relevant skills and resume sections, generates skill-based viva questions, and provides multiple-choice question (MCQ) practice with automated evaluation and attempt history.

## 2. Objectives

- Analyze resumes uploaded in PDF format.
- Extract skills and important resume sections.
- Generate viva questions based on identified skills.
- Provide MCQ-based practice for technical preparation.
- Evaluate submitted answers and calculate scores.
- Store and display previous MCQ attempts.
- Provide a dashboard for viewing practice analytics.

## 3. Features

- PDF resume upload and analysis.
- Resume text extraction using PyMuPDF.
- Skill and section extraction.
- Rule-based viva question generation.
- MCQ generation and evaluation.
- Question-wise feedback and score calculation.
- MCQ attempt history.
- Dashboard with practice analytics.
- REST API using FastAPI.
- PostgreSQL database integration.
- Automated tests using pytest.
- Interactive frontend using Streamlit.

## 4. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Frontend Framework | Streamlit |
| Database | PostgreSQL |
| PDF Processing | PyMuPDF |
| Data Validation | Pydantic |
| Testing Framework | pytest |
| API Testing | Swagger UI |
| API Communication | HTTP/REST |

## 5. System Modules

### Resume Analysis
Accepts a PDF resume, extracts its text, and identifies relevant skills and sections.

### Viva Preparation
Generates questions based on the skills identified from the resume to support viva and interview preparation.

### MCQ Practice
Generates multiple-choice questions, accepts answers, evaluates submissions, and displays performance feedback.

### MCQ History
Displays previous MCQ attempts, including scores and question statistics.

### Dashboard
Presents a summary of available practice analytics and recent MCQ performance.

## 6. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/upload` | Upload and analyze a resume |
| POST | `/mcqs` | Generate MCQs |
| POST | `/mcqs/evaluate/combined` | Evaluate submitted MCQ answers |
| GET | `/mcq-attempts` | Retrieve MCQ attempt history |

For interactive API documentation, open `/docs` after starting the FastAPI server.

## 7. Project Structure

```text
resume-viva-ai/
├── app/
│   ├── api/
│   ├── database/
│   ├── models/
│   ├── services/
│   ├── utils/
│   ├── db_connection.py
│   └── main.py
├── data/
├── docs/
├── frontend/
│   └── streamlit_app.py
├── storage/
├── tests/
├── init_db.py
├── README.md
├── requirements.txt
└── .env
```

## 8. Prerequisites

- Python installed.
- PostgreSQL installed and running.
- A configured database.
- A Python virtual environment.
- Required Python packages installed.

## 9. Setup and Execution

### Step 1: Open the project directory

Open a terminal in the project root directory.

### Step 2: Activate the virtual environment

On Windows PowerShell:

```powershell
.\myenv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

After adding the project's dependencies to `requirements.txt`, run:

```powershell
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Configure the database connection and other required settings in `.env`. Do not commit passwords, API keys, or other secrets to version control.

### Step 5: Initialize the database

If required by the project's setup:

```powershell
python init_db.py
```

### Step 6: Start the backend

```powershell
uvicorn app.main:app --reload
```

Backend API base URL:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Step 7: Start the frontend

Open a second terminal, activate the virtual environment, and run:

```powershell
streamlit run frontend/streamlit_app.py
```

### Step 8: Run automated tests

From the project root:

```powershell
python -m pytest -v
```

## 10. Testing

The project test suite has been executed successfully, with **53 tests passed** at the latest reported run.

Manual edge-case checks completed:

- Empty MCQ answers.
- Invalid PDF upload.
- MCQ history persistence.

Run the test suite again after making code changes.

## 11. Expected Outcome

The application provides a unified platform for resume analysis and technical viva preparation. It helps users identify skills from their resumes, practice relevant questions, evaluate MCQ performance, and review previous attempts.

## 12. Future Enhancements

- Integrate an advanced NLP or large language model for more contextual question generation.
- Improve resume scoring and personalized recommendations.
- Add user authentication and individual progress tracking.
- Expand support for additional resume formats.
- Add more detailed analytics and downloadable reports.

## 13. Conclusion

The AI-Powered Resume Analysis and Viva Preparation System combines resume parsing, skill extraction, question generation, MCQ evaluation, and performance tracking in one application. It provides a foundation for supporting students in technical interview and viva preparation.
