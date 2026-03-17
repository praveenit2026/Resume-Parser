from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import PyPDF2
import docx
import io
import json
import os
import re
from typing import Optional
import httpx

# Load environment variables from .env file
load_dotenv()

SAMBANOVA_BASE_URL = os.environ.get("SAMBANOVA_BASE_URL", "https://api.sambanova.ai/v1")
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_MODEL = os.environ.get("SAMBANOVA_MODEL", "Meta-Llama-3.1-70B-Instruct")

app = FastAPI(
    title="Resume Matcher API",
    description=f"AI-powered resume vs job description matcher using SambaNova ({SAMBANOVA_MODEL})",
    version="1.0.0",
)

# CORS — allow local frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────

class MatchResult(BaseModel):
    score: int
    verdict: str
    summary: str
    matchedSkills: list[str]
    missingSkills: list[str]
    suggestions: list[str]
    experienceAlignment: str
    educationAlignment: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(para.text for para in doc.paragraphs)


def extract_resume_text(file: UploadFile, raw_bytes: bytes) -> str:
    name = (file.filename or "").lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(raw_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(raw_bytes)
    else:
        return raw_bytes.decode("utf-8", errors="replace")


def parse_llm_json(text: str) -> dict:
    # Look for JSON structure in case of preamble
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        clean = match.group(0)
    else:
        clean = re.sub(r"```(?:json)?|```", "", text).strip()
    return json.loads(clean)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Resume Matcher API (SambaNova) is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "engine": "sambanova", "model": SAMBANOVA_MODEL}


@app.post("/api/analyze", response_model=MatchResult)
async def analyze_resume(
    job_description: str = Form(...),
    resume_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Analyze resume against job description using SambaNova Cloud.
    Accepts either a file upload or raw resume text.
    """

    if not SAMBANOVA_API_KEY:
        raise HTTPException(status_code=500, detail="SAMBANOVA_API_KEY is not set in environment.")

    # ── Extract resume content ────────────────────────────────────────────────
    if file and file.filename:
        raw = await file.read()
        resume = extract_resume_text(file, raw)
    elif resume_text:
        resume = resume_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Provide a resume file or resume_text.")

    if len(resume) < 50:
        raise HTTPException(status_code=422, detail="Resume text is too short to analyze.")

    # ── Build prompt ──────────────────────────────────────────────────────────
    prompt = f"""You are an expert ATS system and career coach with 15 years of experience in technical recruiting.
Analyze the resume below against the job description and return ONLY valid JSON — no markdown, no preamble, no explanation outside the JSON.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

Return this exact JSON schema:
{{
  "score": <integer 0-100, ATS compatibility score>,
  "verdict": "<one of: Strong Match | Good Match | Partial Match | Weak Match>",
  "summary": "<2-3 sentences: overall fit assessment, key strengths, main gaps>",
  "matchedSkills": ["<skill>", ...],
  "missingSkills": ["<skill>", ...],
  "suggestions": [
    "<specific, actionable resume improvement>",
    "<specific, actionable resume improvement>",
    "<specific, actionable resume improvement>",
    "<specific, actionable resume improvement>",
    "<specific, actionable resume improvement>"
  ],
  "experienceAlignment": "<1-2 sentences on how experience level aligns>",
  "educationAlignment": "<1 sentence on education fit>"
}}"""

    # ── Call SambaNova ──────────────────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{SAMBANOVA_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {SAMBANOVA_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": SAMBANOVA_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a professional ATS analyzer. Always respond in pure JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "top_p": 0.1
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"SambaNova API error {response.status_code}: {response.text}")
            
            result_data = response.json()
            raw_text = result_data["choices"][0]["message"]["content"]
            data = parse_llm_json(raw_text)
            return MatchResult(**data)

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Could not connect to SambaNova. Check your internet connection.")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/parse-resume")
async def parse_resume_only(file: UploadFile = File(...)):
    """Extract and return raw text from an uploaded resume file."""
    raw = await file.read()
    try:
        text = extract_resume_text(file, raw)
        return {"filename": file.filename, "text": text, "char_count": len(text)}
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {e}")
