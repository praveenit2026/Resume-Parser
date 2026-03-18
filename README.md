# Resume Matcher — Full Stack AI App

An AI-powered resume vs. job description analyzer built with **FastAPI** (backend) and **React + Vite** (frontend), using **SambaNova Cloud** (Meta Llama) for intelligent analysis.

```
┌─────────────────┐      HTTP       ┌───────────────────┐
│   React + Vite  │ ─────────────▶  │   FastAPI Backend  │
│   (port 5173)   │ ◀─────────────  │   (port 8000)      │
└─────────────────┘   JSON result   └────────┬──────────┘
                                             │
                                     SambaNova Cloud API
                                             │
                                     ┌───────▼───────────┐
                                     │  Match Score &     │
                                     │  Skill Analysis    │
                                     └───────────────────┘
```

## Features

- Upload resume as **PDF**, **DOCX**, or **TXT** — or paste text directly
- Paste any job description
- Instant **ATS score** (0–100) with verdict
- **Matched vs. missing skills** breakdown
- **Experience & education alignment** analysis
- **5 actionable coaching suggestions**

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [SambaNova Cloud API key](https://cloud.sambanova.ai/)

---

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.example .env
# Edit .env and add your SAMBANOVA_API_KEY

# Run the server
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

---

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies /api → localhost:8000)
npm run dev
```

App runs at: http://localhost:5173

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Health check |
| POST | `/api/analyze` | Analyze resume vs JD |
| POST | `/api/parse-resume` | Extract text from uploaded file |

### POST `/api/analyze`

**Form data:**

| Field | Type | Required |
|-------|------|----------|
| `job_description` | string | ✅ |
| `file` | file (.pdf/.docx/.txt) | either/or |
| `resume_text` | string | either/or |

**Response:**

```json
{
  "score": 78,
  "verdict": "Good Match",
  "summary": "Strong technical background with most required skills...",
  "matchedSkills": ["Python", "FastAPI", "REST API", "PostgreSQL"],
  "missingSkills": ["Kubernetes", "GraphQL"],
  "suggestions": [
    "Add specific metrics to your work experience bullets...",
    ...
  ],
  "experienceAlignment": "5 years of backend experience aligns well with the senior role...",
  "educationAlignment": "CS degree meets the requirement."
}
```

---

## Deployment

This project is configured for automated deployment on **Render** using a single Blueprint (`render.yaml`).

### Deploy Steps

1. Create an account on [Render](https://render.com).
2. Go to your Dashboard → **New** → **Blueprint**.
3. Connect your GitHub repository containing this project.
4. Render will automatically detect the `render.yaml` file and create two services:
   - `resume-matcher-backend` (Docker web service)
   - `resume-matcher-frontend` (Static Site)
5. During setup, configure the following Environment Variables:

**Backend (`resume-matcher-backend`):**
- `SAMBANOVA_API_KEY`: Your SambaNova Cloud API key
- `SAMBANOVA_BASE_URL`: `https://api.sambanova.ai/v1` (optional, default provided)
- `SAMBANOVA_MODEL`: `Meta-Llama-3.1-8B-Instruct` (optional, default provided)
- `ENDEE_URL`: The URL of your Endee Vector DB (if using one, otherwise leave blank)

**Frontend (`resume-matcher-frontend`):**
- `VITE_API_URL`: Set this to your backend's Render URL (e.g., `https://resume-matcher-backend-xxxx.onrender.com`). *Note: Set this after the backend is created.*

6. Click **Apply** to deploy both services automatically!
