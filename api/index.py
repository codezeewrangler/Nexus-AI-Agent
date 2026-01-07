# Vercel Serverless Entry Point
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Response, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import json

# Initialize FastAPI
app = FastAPI(title="Nexus AI Agent")

# Pydantic models
class AgentRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    output_format: Optional[str] = "markdown"


# Simple in-memory store for Vercel (no persistent storage)
documents_content = {}


@app.get("/")
async def root():
    """Serve the frontend"""
    html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return HTMLResponse("<h1>Nexus AI Agent</h1><p>Go to /docs for API</p>")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.post("/run_agent_markdown")
async def run_agent_markdown(request: AgentRequest):
    """
    Simplified agent for Vercel serverless.
    Uses OpenAI directly without FAISS (which has binary dependencies).
    """
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return Response(
            content="OPENAI_API_KEY not configured",
            status_code=500
        )
    
    client = OpenAI(api_key=api_key)
    
    # Build context from any uploaded documents
    context = "\n\n".join(documents_content.values()) if documents_content else ""
    
    # Determine mode
    if len(context) >= 500:
        # Strict mode - document only
        system_prompt = """You are a document summarization assistant.
Summarize ONLY what is in the provided document context.
Do NOT add external information."""
    else:
        # Hybrid mode - can use general knowledge
        system_prompt = """You are a helpful research assistant.
If document context is provided, prefer using it.
You may supplement with your own knowledge if needed."""
    
    user_prompt = f"""
Document Context:
{context if context else "No documents uploaded."}

Query: {request.query}

Provide a well-structured markdown response with:
# Title
## Summary
## Key Points
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


@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """
    Store document content in memory (Vercel has no persistent storage).
    """
    content = await file.read()
    
    # Parse based on file type
    filename = file.filename.lower()
    
    if filename.endswith(".txt"):
        text = content.decode("utf-8")
    elif filename.endswith(".pdf"):
        # Simple text extraction for PDFs
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() for page in reader.pages)
        except:
            text = "[PDF parsing not available]"
    elif filename.endswith(".docx"):
        try:
            from docx import Document
            import io
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
        except:
            text = "[DOCX parsing not available]"
    else:
        return Response(content="Unsupported file type", status_code=400)
    
    documents_content[file.filename] = text
    
    return {"message": "Document uploaded", "filename": file.filename}


# Vercel handler
handler = app
