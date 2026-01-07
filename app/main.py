# app/main.py

from dotenv import load_dotenv
load_dotenv()  # load .env early

import os
import shutil
from fastapi import FastAPI, Response, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.models import AgentRequest, AgentResponse
from app.agent.graph import run_agent_graph
from app.agent.rag import build_vector_store

app = FastAPI(title="AI Task Automation Agent")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Document upload directory
UPLOAD_DIR = "data/documents"


@app.get("/")
def root():
    """Serve the frontend"""
    return FileResponse("static/index.html")


@app.get("/favicon.ico")
def favicon():
    """Return empty response for favicon requests"""
    return Response(status_code=204)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF, TXT, DOCX) and rebuild the vector store.
    """
    # Validate file type
    allowed_extensions = {".pdf", ".txt", ".docx"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return Response(
            content="Invalid file type. Allowed: PDF, TXT, DOCX",
            status_code=400
        )
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Rebuild vector store
    try:
        build_vector_store()
    except Exception as e:
        return Response(
            content=f"File uploaded but vector store rebuild failed: {str(e)}",
            status_code=500
        )
    
    return {"message": "File uploaded and indexed successfully", "filename": file.filename}


@app.post("/run_agent_markdown")
async def run_agent_markdown(request: AgentRequest):
    """
    Returns ONLY the markdown report (text/markdown), without JSON wrapping.
    """
    report, _ = await run_agent_graph(
        query=request.query,
        user_id=request.user_id,
        output_format=request.output_format,
    )

    return Response(content=report, media_type="text/markdown")

