# Nexus AI Agent v2.0

**Production-Grade RAG System for Document Q&A**

## What This Actually Is

A Retrieval-Augmented Generation (RAG) system that:
- Uploads and processes PDF/DOCX/TXT documents
- Splits documents into semantic chunks
- Generates embeddings using Google Gemini
- Stores embeddings in ChromaDB vector database
- Retrieves relevant context for user queries
- Generates answers with source citations

## Architecture

```
User → FastAPI → Document Parser → Chunker → Embeddings → ChromaDB
                                                              ↓
User ← FastAPI ← LLM (Gemini) ← Context Retrieval ← Vector Search
```

### Project Structure

```
nexus/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_service.py    # Document parsing
│   │   ├── embedding_service.py   # Embedding generation (Gemini)
│   │   ├── vector_service.py      # Vector DB operations (ChromaDB)
│   │   └── llm_service.py         # LLM calls (Gemini)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── logging.py             # Logging config
│   └── utils/
│       ├── __init__.py
│       └── chunking.py            # Text chunking
├── tests/
│   ├── __init__.py
│   ├── test_chunking.py
│   ├── test_document_service.py
│   └── test_api.py
├── data/
│   ├── documents/                 # Uploaded files
│   └── chroma/                    # Vector DB storage
├── static/
│   ├── index.html
│   └── styles.css
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Embeddings**: Google Gemini text-embedding-004
- **LLM**: Google Gemini 2.0 Flash
- **Vector Database**: ChromaDB
- **Document Processing**: PyPDF2, python-docx
- **Caching**: Redis (optional)

## Installation

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/nexus-ai-agent.git
cd nexus-ai-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run development server
uvicorn app.main:app --reload
```

### Docker Deployment

```bash
# Set your API key
export GEMINI_API_KEY=your_key_here

# Run with Docker Compose
docker-compose up -d
```

## API Usage

### RAG Endpoints (New)

#### Upload Document with RAG Processing
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf"
```

Response:
```json
{
  "document_id": "uuid-here",
  "filename": "document.pdf",
  "size_bytes": 12345,
  "chunk_count": 42,
  "upload_time": "2026-01-29T12:00:00Z"
}
```

#### Query Documents (RAG)
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the refund policy?",
    "top_k": 5
  }'
```

Response:
```json
{
  "answer": "According to the documents...",
  "sources": [
    {
      "content": "Our refund policy states...",
      "similarity": 0.92,
      "chunk_id": "doc123_chunk_5",
      "page_number": 3
    }
  ],
  "query_time_ms": 1234,
  "model_used": "gemini-2.0-flash",
  "tokens_used": 500
}
```

#### Health Check
```bash
curl http://localhost:8000/api/health
```

### Legacy Endpoints (Backward Compatible)

#### Simple Upload (No RAG)
```bash
curl -X POST http://localhost:8000/upload_document \
  -F "file=@document.pdf"
```

#### Simple Query (No RAG)
```bash
curl -X POST http://localhost:8000/run_agent_markdown \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize the documents"}'
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app

# Run specific test file
pytest tests/test_chunking.py -v
```

## Configuration

All configuration is done via environment variables. See `.env.example` for all options:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Required |
| `CHROMA_PERSIST_DIRECTORY` | Path to ChromaDB storage | `./data/chroma` |
| `CHUNK_SIZE` | Characters per chunk | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `TOP_K_CHUNKS` | Number of chunks to retrieve | `5` |
| `LLM_MODEL` | Gemini model to use | `gemini-2.0-flash` |

## Known Limitations

- Only supports English text
- Large documents (>100 pages) may take 30+ seconds to process
- Requires Google Gemini API key (free tier available)
- ChromaDB persistence can be slow on some systems

## Future Improvements

- [ ] Support for more file types (EPUB, Markdown)
- [ ] Multi-language support
- [ ] Streaming responses
- [ ] Better chunking strategies (semantic chunking)
- [ ] Hybrid search (keyword + vector)
- [ ] User authentication
- [ ] Rate limiting
- [ ] Metrics and monitoring

## License

MIT License
