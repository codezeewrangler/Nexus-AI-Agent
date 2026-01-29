# app/api/routes.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import (
    DocumentUploadResponse, 
    QueryRequest, 
    QueryResponse,
    SourceChunk,
    HealthResponse
)
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
from app.utils.chunking import TextChunker
from app.core.exceptions import (
    FileValidationError,
    DocumentParsingError,
    VectorStoreError,
    LLMError,
    EmbeddingGenerationError
)
import logging
import uuid
import time
from datetime import datetime
from io import BytesIO

logger = logging.getLogger("nexus")
router = APIRouter()


def get_services():
    """Lazy initialization of services"""
    return {
        'doc_service': DocumentService(),
        'embedding_service': EmbeddingService(),
        'vector_service': VectorService(),
        'llm_service': LLMService(),
        'chunker': TextChunker()
    }


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document
    
    Steps:
    1. Validate file
    2. Parse document
    3. Chunk text
    4. Generate embeddings
    5. Store in vector database
    """
    services = get_services()
    doc_service = services['doc_service']
    embedding_service = services['embedding_service']
    vector_service = services['vector_service']
    chunker = services['chunker']
    
    try:
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Read file
        contents = await file.read()
        file_size = len(contents)
        
        # Validate
        doc_service.validate_file(file.filename, file_size)
        
        # Parse document
        file_obj = BytesIO(contents)
        document_data = doc_service.parse_document(file.filename, file_obj)
        
        # Chunk
        chunks = chunker.chunk_document(document_data)
        
        if not chunks:
            raise DocumentParsingError("No content could be extracted from the document")
        
        # Generate embeddings
        chunks_with_embeddings = embedding_service.embed_chunks(chunks)
        
        # Store in vector database
        vector_service.add_document(document_id, chunks_with_embeddings)
        
        logger.info(f"Successfully processed document {file.filename} with {len(chunks)} chunks")
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            size_bytes=file_size,
            chunk_count=len(chunks),
            upload_time=datetime.utcnow()
        )
        
    except FileValidationError as e:
        logger.warning(f"File validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except DocumentParsingError as e:
        logger.error(f"Document parsing failed: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except EmbeddingGenerationError as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except VectorStoreError as e:
        logger.error(f"Vector store operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query documents and get AI-generated answer
    
    Steps:
    1. Generate query embedding
    2. Search vector database for similar chunks
    3. Pass chunks to LLM for answer generation
    """
    services = get_services()
    embedding_service = services['embedding_service']
    vector_service = services['vector_service']
    llm_service = services['llm_service']
    
    try:
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = embedding_service.generate_query_embedding(request.query)
        
        # Search vector database
        similar_chunks = vector_service.search(
            query_embedding=query_embedding,
            top_k=request.top_k,
            document_id=request.document_id,
            min_similarity=0.5  # Filter low-quality results
        )
        
        if not similar_chunks:
            return QueryResponse(
                answer="I couldn't find relevant information in the documents to answer your question.",
                sources=[],
                query_time_ms=int((time.time() - start_time) * 1000),
                model_used="N/A",
                tokens_used=0
            )
        
        # Generate answer
        llm_result = llm_service.generate_answer(request.query, similar_chunks)
        
        # Format sources
        sources = [
            SourceChunk(
                content=chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                similarity=chunk['similarity'],
                chunk_id=chunk['chunk_id'],
                page_number=chunk['metadata'].get('page_number')
            )
            for chunk in similar_chunks
        ]
        
        query_time = int((time.time() - start_time) * 1000)
        
        return QueryResponse(
            answer=llm_result['answer'],
            sources=sources,
            query_time_ms=query_time,
            model_used=llm_result['metadata']['model'],
            tokens_used=llm_result['metadata']['tokens_used']
        )
        
    except EmbeddingGenerationError as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except VectorStoreError as e:
        logger.error(f"Vector search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except LLMError as e:
        logger.error(f"LLM generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Query failed")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        services = get_services()
        vector_service = services['vector_service']
        return HealthResponse(
            status="healthy",
            documents_stored=vector_service.get_document_count()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            documents_stored=0
        )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the vector store"""
    try:
        services = get_services()
        vector_service = services['vector_service']
        vector_service.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except VectorStoreError as e:
        logger.error(f"Delete failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
