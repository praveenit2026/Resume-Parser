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
import hashlib
from typing import Optional
import httpx

# Load environment variables from .env file
load_dotenv(override=True)

# Support SambaNova (preferred) or OpenAI as fallback
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if SAMBANOVA_API_KEY:
    API_KEY = SAMBANOVA_API_KEY
    API_BASE_URL = os.environ.get("SAMBANOVA_BASE_URL", "https://api.sambanova.ai/v1")
    AI_MODEL = os.environ.get("SAMBANOVA_MODEL", "Meta-Llama-3.1-8B-Instruct")
    AI_ENGINE = "sambanova"
else:
    API_KEY = OPENAI_API_KEY
    API_BASE_URL = "https://api.openai.com/v1"
    AI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    AI_ENGINE = "openai"

# ── Endee Vector DB Setup ─────────────────────────────────────────────────────
ENDEE_URL = os.environ.get("ENDEE_URL", "http://localhost:8080")
ENDEE_TOKEN = os.environ.get("ENDEE_AUTH_TOKEN", "")
ENDEE_INDEX = "resumes"
EMBEDDING_DIM = 384   # all-MiniLM-L6-v2 output dimension

_endee_client = None
_endee_index = None
_embedder = None

def get_embedder():
    """Returns a dummy embedder function to avoid OOM on Render free tier."""
    global _embedder
    if _embedder is None:
        # Mock embedder to save 500MB+ RAM
        _embedder = lambda text: [0.1] * EMBEDDING_DIM
    return _embedder

def get_endee():
    """Lazy-connect to Endee and return (client, index)."""
    global _endee_client, _endee_index
    if _endee_client is None:
        from endee import Endee, Precision
        from endee.schema import VectorItem
        
        # Monkeypatch VectorItem to fix SDK bug in upsert (calls .get() on VectorItem)
        if not hasattr(VectorItem, "get"):
            VectorItem.get = lambda self, key, default=None: getattr(self, key, default)
            
        _endee_client = Endee(ENDEE_TOKEN) if ENDEE_TOKEN else Endee()
        _endee_client.set_base_url(f"{ENDEE_URL}/api/v1")
        # Create index if it doesn't exist
        try:
            _endee_client.create_index(
                name=ENDEE_INDEX,
                dimension=EMBEDDING_DIM,
                space_type="cosine",
                precision=Precision.INT8,
            )
        except Exception:
            pass  # Index likely already exists
        _endee_index = _endee_client.get_index(name=ENDEE_INDEX)
    return _endee_client, _endee_index

def embed_text(text: str) -> list[float]:
    """Convert text to a vector embedding (Mocked for Render free tier)."""
    model = get_embedder()
    # return a dummy vector to bypass Heavy ML loading
    return model(text)

def store_resume_in_endee(doc_id: str, text: str, meta: dict):
    """Upsert a resume embedding into Endee."""
    try:
        _, index = get_endee()
        vector = embed_text(text[:2000])  # embed first 2000 chars
        index.upsert([{"id": doc_id, "vector": vector, "meta": meta}])
    except Exception as e:
        print(f"[Endee] Warning: could not store resume embedding: {e}")

def find_similar_resumes(query_text: str, top_k: int = 3) -> list[dict]:
    """Search Endee for resumes similar to the query."""
    try:
        _, index = get_endee()
        vector = embed_text(query_text[:2000])
        results = index.query(vector=vector, top_k=top_k)
        return results
    except Exception as e:
        print(f"[Endee] Warning: vector search failed: {e}")
        return []

# ── App Setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Resume Matcher API",
    description=f"AI-powered resume vs job description matcher using {AI_ENGINE} ({AI_MODEL}) + Endee vector DB",
    version="2.0.0",
)

# CORS — allow all origins for dev and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    # Remove control characters that LLMs sometimes inject into JSON strings
    clean = re.sub(r'[\x00-\x1f\x7f](?<!")', lambda m: ' ' if m.group() in ('\n', '\r', '\t') else '', clean)
    return json.loads(clean)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Resume Matcher API is running", "version": "2.0.0", "vector_db": "Endee"}


@app.get("/health")
def health():
    endee_ok = False
    try:
        get_endee()
        endee_ok = True
    except Exception:
        pass
    return {
        "status": "healthy",
        "engine": AI_ENGINE,
        "model": AI_MODEL,
        "endee": "connected" if endee_ok else "unavailable",
    }


@app.post("/api/analyze", response_model=MatchResult)
async def analyze_resume(
    job_description: str = Form(...),
    resume_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Analyze resume against job description using AI + Endee vector DB.
    Accepts either a file upload or raw resume text.
    """

    if not API_KEY:
        raise HTTPException(status_code=500, detail="No API key set. Please set SAMBANOVA_API_KEY or OPENAI_API_KEY in .env")

    # ── Extract resume content ────────────────────────────────────────────────
    filename = ""
    if file and file.filename:
        raw = await file.read()
        resume = extract_resume_text(file, raw)
        filename = file.filename or ""
    elif resume_text:
        resume = resume_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Provide a resume file or resume_text.")

    if len(resume) < 50:
        raise HTTPException(status_code=422, detail="Resume text is too short to analyze.")

    # ── Store resume embedding in Endee ───────────────────────────────────────
    doc_id = hashlib.md5(resume.encode()).hexdigest()
    store_resume_in_endee(
        doc_id=doc_id,
        text=resume,
        meta={"filename": filename, "char_count": len(resume)},
    )

    # ── Find similar past resumes from Endee (for context) ────────────────────
    similar = find_similar_resumes(job_description, top_k=3)
    similar_context = ""
    if similar:
        similar_context = "\n\nNOTE: Similar resumes have been retrieved from the vector database for context."

    # ── Build prompt ──────────────────────────────────────────────────────────
    prompt = f"""You are an expert ATS system and career coach with 15 years of experience in technical recruiting.
Analyze the resume below against the job description and return ONLY valid JSON — no markdown, no preamble, no explanation outside the JSON.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}{similar_context}

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

    # ── Call AI API (SambaNova or OpenAI) ─────────────────────────────────────
    try:
        url = f"{API_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": AI_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
        }
        # Only add JSON response format for OpenAI (SambaNova may not support it)
        if AI_ENGINE == "openai":
            payload["response_format"] = {"type": "json_object"}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"{AI_ENGINE} API error {response.status_code}: {response.text}")
            
            result_data = response.json()
            try:
                raw_text = result_data["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                raise HTTPException(status_code=500, detail=f"Unexpected response format: {result_data}")
                
            data = parse_llm_json(raw_text)
            return MatchResult(**data)

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Could not connect to AI API. Check your internet connection.")
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


@app.get("/api/vector-db/status")
def vector_db_status():
    """Check Endee vector DB connectivity and index info."""
    try:
        _, index = get_endee()
        return {"status": "connected", "index": ENDEE_INDEX, "url": ENDEE_URL}
    except Exception as e:
        return {"status": "unavailable", "error": str(e), "url": ENDEE_URL}
