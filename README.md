# AI-Powered Resume Analysis and Viva Preparation System

A Python-based web application that helps students analyze their resumes, identify technical skills, prepare for viva examinations, and practice technical MCQs with automated evaluation and performance tracking.

## Overview

The AI-Powered Resume Analysis and Viva Preparation System combines resume parsing, skill extraction, viva question generation, MCQ practice, and performance tracking in a single application.

Users can upload a PDF resume, review the extracted information, generate viva questions based on their skills, practice multiple-choice questions, and review their previous attempts.

The application uses a **Streamlit frontend**, a **FastAPI backend**, and a **PostgreSQL database**. Docker support is available for running the frontend and backend in separate containers.

## Features

- **PDF Resume Analysis** — Upload resumes and extract text using PyMuPDF.
- **Skill Extraction** — Identify relevant technical skills and resume sections.
- **Viva Preparation** — Generate rule-based and AI-generated viva questions.
- **MCQ Practice** — Generate technical multiple-choice questions.
- **Automated Evaluation** — Calculate scores and provide question-wise feedback.
- **MCQ History** — Store and review previous practice attempts.
- **Dashboard** — View available practice statistics and performance summaries.
- **REST API** — Expose application functionality through FastAPI.
- **Database Persistence** — Store resume records, MCQ attempts, and AI viva questions in PostgreSQL.
- **Automated Testing** — Test application behavior using pytest.
- **Docker Support** — Run the backend and frontend in separate containers using Docker Compose.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | PostgreSQL |
| PDF Processing | PyMuPDF |
| Data Validation | Pydantic |
| API Communication | HTTP/REST |
| API Documentation | Swagger UI |
| Testing | pytest |
| Containerization | Docker |
| Container Orchestration | Docker Compose |

## Application Workflow

1. Upload a PDF resume through the Streamlit interface.
2. Extract and analyze resume text through the backend.
3. Identify technical skills and relevant resume sections.
4. Generate viva questions based on the resume information.
5. Practice MCQs and submit answers for evaluation.
6. Review scores, feedback, and previous attempts.

## Project Structure

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
│   ├── Dockerfile
│   └── streamlit_app.py
├── storage/
├── tests/
├── .dockerignore
├── .gitignore
├── Dockerfile
├── compose.yaml
├── init_db.py
├── requirements.txt
└── README.md
```

## Prerequisites

### For local development

- Python
- PostgreSQL
- Git
- A configured PostgreSQL database
- A Python virtual environment

### For Docker

- Docker Desktop with Docker Compose
- A configured PostgreSQL database accessible to the backend container

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/sahilsharma-software/resume-viva-ai.git
cd resume-viva-ai
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root and configure the PostgreSQL connection string and any other environment variables required by the application.

For Docker Compose, the database host must be reachable from the API container. If PostgreSQL is running directly on the Windows host, use `host.docker.internal` as the database hostname.

For example, the connection string follows this general format:

```text
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@host.docker.internal:5432/resume_viva_db
```

Replace the placeholder credentials with your own values and use the database name configured for your environment.

**Security:** Never commit `.env` files, database passwords, API keys, or other secrets to version control.

### 5. Initialize the database

If required by your configuration, run:

```powershell
python init_db.py
```

### 6. Start the backend

```powershell
uvicorn app.main:app --reload
```

Backend URL: http://127.0.0.1:8000

Interactive API documentation: http://127.0.0.1:8000/docs

### 7. Start the frontend

Open a second terminal, activate the virtual environment, and run:

```powershell
streamlit run frontend/streamlit_app.py
```

Use the Streamlit interface to analyze resumes, prepare viva questions, practice MCQs, and review previous attempts.

## Running with Docker

Docker Compose runs the FastAPI backend and Streamlit frontend as separate containers.

### 1. Configure the database

Ensure the `.env` file contains the required environment variables and a valid PostgreSQL connection string. When PostgreSQL runs on the host machine, use `host.docker.internal` as the database hostname.

### 2. Build and start the containers

From the project root, run:

```powershell
docker compose up -d --build
```

This builds the images and starts the services in the background.

### 3. Check container status

```powershell
docker compose ps
```

Both the API and frontend containers should show a running status.

### 4. Access the application

- **Streamlit frontend:** http://localhost:8601
- **FastAPI backend:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs

The frontend communicates with the backend through the Docker Compose service address configured by the `API_URL` environment variable.

### 5. View logs

To view logs for both services:

```powershell
docker compose logs
```

To view logs for a specific service:

```powershell
docker compose logs api
docker compose logs frontend
```

### 6. Stop the containers

```powershell
docker compose down
```

This stops and removes the Compose containers and network. It does not delete the PostgreSQL database running separately on the host machine.

## API Documentation

The FastAPI backend provides endpoints for resume processing, MCQ generation and evaluation, viva preparation, and related application functionality.

Open http://127.0.0.1:8000/docs while the backend is running to inspect the available routes, request schemas, and response formats.

## Testing

Run the automated test suite from the project root:

```powershell
python -m pytest -v
```

**Latest previously reported test result: 54 passed.**

Run the test suite again after code changes to verify that existing functionality remains stable.

## Future Improvements

- More contextual and personalized viva question generation
- Enhanced resume analysis and skill recommendations
- User authentication and individual progress tracking
- Support for additional resume formats
- Downloadable performance reports and expanded analytics

## Conclusion

The AI-Powered Resume Analysis and Viva Preparation System provides a unified platform for resume analysis and technical preparation. It combines PDF text extraction, skill identification, viva question generation, MCQ evaluation, and performance tracking to support students preparing for technical interviews and viva examinations.

The project also includes Docker support for running its frontend and backend in separate containers.

## Application Screenshots

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)
