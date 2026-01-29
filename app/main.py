# app/main.py
# Nexus AI Agent - Production-Grade RAG System

from dotenv import load_dotenv
load_dotenv()

import os
import shutil
from fastapi import FastAPI, Response, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import setup_logging

# Configure logging
logger = setup_logging()

# Create app
app = FastAPI(
    title="Nexus AI Agent",
    description="RAG-based Document Q&A System",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include RAG API routes
app.include_router(router, prefix="/api")

# Document storage for legacy endpoints
UPLOAD_DIR = "data/documents"


# ============== Legacy Pydantic Models ==============
class AgentRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    output_format: Optional[str] = "markdown"


# ============== Legacy Helper Functions ==============
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


# ============== Root and Static Routes ==============
@app.get("/")
def root():
    """Serve the frontend"""
    return FileResponse("static/index.html")


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.get("/health")
def health_check():
    """Legacy health check - redirects to API health"""
    return {"status": "ok", "version": "2.0.0"}


# ============== Legacy Endpoints (for backward compatibility) ==============
@app.post("/upload_document")
async def upload_document_legacy(file: UploadFile = File(...)):
    """Legacy upload endpoint - saves to disk only (no RAG processing)"""
    allowed_extensions = {".pdf", ".txt", ".docx"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return Response(content="Invalid file type", status_code=400)
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logger.info(f"Legacy upload: {file.filename}")
    return {"message": "File uploaded successfully", "filename": file.filename}


@app.post("/run_agent_markdown")
async def run_agent_markdown(request: AgentRequest):
    """Legacy agent endpoint - uses simple context injection (no RAG)"""
    import google.generativeai as genai
    
    settings = get_settings()
    api_key = settings.gemini_api_key
    
    if not api_key:
        return Response(content="GEMINI_API_KEY not configured", status_code=500)
    
    # Configure Gemini API
    genai.configure(api_key=api_key)
    
    # Load all documents
    context = get_all_documents()
    context_length = len(context.strip())
    
    # Determine mode based on context
    if context_length >= 500:
        system_instruction = """You are a document summarization assistant.
Summarize ONLY what is in the provided document context.
Do NOT add external information or recommendations not in the documents."""
    else:
        system_instruction = """You are a helpful research assistant.
If document context is provided, prefer using it.
You may supplement with your own knowledge if the documents are insufficient."""
    
    user_prompt = f"""
Document Context:
{context if context else "No documents uploaded."}

Query: {request.query}

Provide a well-structured markdown response with:
# Title
## Summary
## Key Points (use bullet points)
"""
    
    # Create Gemini model with system instruction
    model = genai.GenerativeModel(
        model_name=settings.llm_model,
        system_instruction=system_instruction
    )
    
    response = model.generate_content(user_prompt)
    report = response.text
    
    logger.info(f"Legacy query processed: {request.query[:50]}...")
    return Response(content=report, media_type="text/markdown")


# ============== App Events ==============
@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    logger.info("Starting Nexus AI Agent v2.0...")
    logger.info(f"Using embedding model: {settings.embedding_model}")
    logger.info(f"Using LLM model: {settings.llm_model}")
    logger.info(f"Vector DB directory: {settings.chroma_persist_directory}")
    
    # Create data directories
    os.makedirs(settings.chroma_persist_directory, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Nexus AI Agent...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
