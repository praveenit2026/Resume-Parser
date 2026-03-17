# Resume Matcher — Full Stack AI App

An AI-powered resume vs. job description analyzer built with **FastAPI** (backend) and **React + Vite** (frontend), using **Claude** (Anthropic) for intelligent analysis.

```
┌─────────────────┐      HTTP       ┌───────────────────┐
│   React + Vite  │ ─────────────▶  │   FastAPI Backend  │
│   (port 5173)   │ ◀─────────────  │   (port 8000)      │
└─────────────────┘   JSON result   └────────┬──────────┘
                                             │
                                    Anthropic API (Claude)
                                             │
                                    ┌────────▼──────────┐
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
- An [Anthropic API key](https://console.anthropic.com/)

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
# Edit .env and add your ANTHROPIC_API_KEY

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

## Project Structure

```
resume-matcher/
├── backend/
│   ├── main.py              # FastAPI app, routes, Claude integration
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # API key template
│
└── frontend/
    ├── index.html
    ├── vite.config.js       # Dev proxy to :8000
    ├── package.json
    └── src/
        ├── main.jsx
        ├── App.jsx          # Main layout & state
        ├── App.module.css
        ├── index.css        # Global design tokens
        ├── hooks/
        │   └── useApi.js    # Axios API client
        └── components/
            ├── UploadZone.jsx      # Drag & drop + paste input
            ├── ScoreGauge.jsx      # SVG circular score gauge
            └── ResultsPanel.jsx    # Full results display
```

---

## Deployment

### Backend — Railway / Render / Fly.io

1. Set `ANTHROPIC_API_KEY` as an environment variable
2. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend — Vercel / Netlify

1. Set `VITE_API_URL` to your deployed backend URL
2. Update `vite.config.js` proxy or use `axios.defaults.baseURL`
3. `npm run build` → deploy `dist/` folder
