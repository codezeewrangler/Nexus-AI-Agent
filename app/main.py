# app/main.py
# Lightweight version for low-memory deployments (Render Free Tier)

from dotenv import load_dotenv
load_dotenv()

import os
import shutil
from fastapi import FastAPI, Response, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI

app = FastAPI(title="Nexus AI Agent")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Document storage (in-memory for serverless)
UPLOAD_DIR = "data/documents"
documents_cache = {}

# Pydantic models
class AgentRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    output_format: Optional[str] = "markdown"


def load_document(filepath: str) -> str:
    """Load document content based on file type."""
    if filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    elif filepath.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except:
            return ""
    elif filepath.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except:
            return ""
    return ""


def get_all_documents() -> str:
    """Load all documents from the data folder."""
    all_text = []
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith("."):
                continue
            filepath = os.path.join(UPLOAD_DIR, filename)
            content = load_document(filepath)
            if content:
                all_text.append(f"--- Document: {filename} ---\n{content}")
    return "\n\n".join(all_text)


@app.get("/")
def root():
    """Serve the frontend"""
    return FileResponse("static/index.html")


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document."""
    allowed_extensions = {".pdf", ".txt", ".docx"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return Response(content="Invalid file type", status_code=400)
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"message": "File uploaded successfully", "filename": file.filename}


@app.post("/run_agent_markdown")
async def run_agent_markdown(request: AgentRequest):
    """Run the AI agent and return markdown response."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return Response(content="OPENAI_API_KEY not configured", status_code=500)
    
    client = OpenAI(api_key=api_key)
    
    # Load all documents
    context = get_all_documents()
    context_length = len(context.strip())
    
    # Determine mode based on context
    if context_length >= 500:
        # Strict mode - document only
        system_prompt = """You are a document summarization assistant.
Summarize ONLY what is in the provided document context.
Do NOT add external information or recommendations not in the documents."""
        mode = "strict"
    else:
        # Hybrid mode - can use general knowledge
        system_prompt = """You are a helpful research assistant.
If document context is provided, prefer using it.
You may supplement with your own knowledge if the documents are insufficient."""
        mode = "hybrid"
    
    user_prompt = f"""
Document Context:
{context if context else "No documents uploaded."}

Query: {request.query}

Provide a well-structured markdown response with:
# Title
## Summary
## Key Points (use bullet points)
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
    )
    
    report = response.choices[0].message.content
    return Response(content=report, media_type="text/markdown")
