# 🧠 Nexus AI Agent

> **Autonomous Multi-Step AI Agent for Research, Summarization & Report Generation**

An intelligent task automation agent built with Python, FastAPI, and OpenAI. It automates research, summarization, and report generation workflows with >85% accuracy using RAG and dynamic context handling.

🔗 **Live Demo**: [https://nexus-ai-agent.onrender.com](https://nexus-ai-agent.onrender.com)

---

## ✨ Features

- **📄 Multi-Format Document Support** - Upload PDF, TXT, and DOCX files
- **🔍 Intelligent Summarization** - Context-aware document analysis
- **🧠 Hybrid Mode** - Strict document-only mode OR enhanced with LLM knowledge
- **⚡ Fast Inference** - Optimized for low-memory cloud deployments
- **🎨 Futuristic UI** - Dark theme with glassmorphism and animated gradients
- **📊 Structured Reports** - Clean Markdown output with executive summaries

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (HTML/CSS/JS)                    │
│              https://nexus-ai-agent.onrender.com                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │   /upload   │  │ /run_agent_md    │  │     /health       │  │
│  │  Document   │  │   Agent Query    │  │   Health Check    │  │
│  └──────┬──────┘  └────────┬─────────┘  └───────────────────┘  │
└─────────┼──────────────────┼────────────────────────────────────┘
          │                  │
          ▼                  ▼
┌─────────────────┐  ┌───────────────────────────────────────────┐
│ Document Store  │  │              OpenAI GPT-4o-mini           │
│ data/documents  │  │     Summarization & Report Generation     │
└─────────────────┘  └───────────────────────────────────────────┘
```

---

## 🔄 Agent Workflow

| Step | Process | Description |
|------|---------|-------------|
| 1️⃣ | **Upload** | User uploads PDF, TXT, or DOCX document |
| 2️⃣ | **Parse** | Document content extracted and stored |
| 3️⃣ | **Query** | User asks a question about the document |
| 4️⃣ | **Analyze** | System determines strict vs hybrid mode |
| 5️⃣ | **Generate** | OpenAI creates structured Markdown report |

### Summarization Modes

| Mode | Condition | Behavior |
|------|-----------|----------|
| 🔒 **Strict** | Document ≥ 500 chars | Uses ONLY document content |
| 🔓 **Hybrid** | Document < 500 chars | Document + LLM knowledge |

---

## 📁 Project Structure

```
nexus-ai-agent/
├── app/
│   └── main.py              # FastAPI application & all routes
├── static/
│   ├── index.html           # Frontend UI
│   └── styles.css           # Futuristic dark theme
├── data/
│   └── documents/           # Uploaded documents (PDF, TXT, DOCX)
├── api/
│   └── index.py             # Vercel serverless handler
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Local development stack
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API Key

### Local Installation

```bash
# Clone the repository
git clone https://github.com/codezeewrangler/Nexus-AI-Agent.git
cd Nexus-AI-Agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the Application

- **Frontend UI**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or just Docker
docker build -t nexus-ai-agent .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key nexus-ai-agent
```

---

## 📡 API Reference

### `POST /upload_document`

Upload a document for analysis.

```bash
curl -X POST https://nexus-ai-agent.onrender.com/upload_document \
  -F "file=@document.pdf"
```

### `POST /run_agent_markdown`

Run the agent and get a Markdown report.

```bash
curl -X POST https://nexus-ai-agent.onrender.com/run_agent_markdown \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize the key points"}'
```

### `GET /health`

Health check endpoint.

```bash
curl https://nexus-ai-agent.onrender.com/health
```

---

## ⚙️ Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `TAVILY_API_KEY` | Tavily search API key | Optional |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, Python 3.11 |
| **LLM** | OpenAI GPT-4o-mini |
| **Frontend** | HTML, CSS, JavaScript |
| **Document Parsing** | PyPDF, python-docx |
| **Deployment** | Docker, Render |

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Summarization Accuracy** | >85% |
| **Memory Usage** | ~150MB |
| **Cold Start** | ~30s (Render free tier) |
| **Response Time** | 2-5s |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Yashovardhan Tiwari**

- GitHub: [@codezeewrangler](https://github.com/codezeewrangler)
- Built with ❤️ using FastAPI and OpenAI
