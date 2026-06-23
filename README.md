# RAG Support Agent

A conversational AI support agent built for VortexIQ as part of an AI Engineering internship project.

## What it does

- Ingests PDF and web documents into a vector database
- Answers customer support questions using Retrieval Augmented Generation (RAG)
- Refuses to answer out-of-scope questions (hallucination guardrail)
- Detects negative sentiment and escalates frustrated users to human agents
- Provides a real-time chat UI and a human agent dashboard

## Architecture
PDF / Web Docs → Text Chunker → Embedder (all-MiniLM-L6-v2) → ChromaDB

↓

User Query → Embed → Similarity Search → Groq LLaMA 3.1 → Answer

↓

WebSocket → Sentiment (VADER) → Escalation Gateway → Agent Dashboard
## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + uvicorn |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | Groq LLaMA 3.1 8B Instant |
| Sentiment | VADER |
| Frontend | Vanilla HTML/CSS/JS |

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Efrrowini/rag-support-agent.git
cd rag-support-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate    # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Create a `.env` file in the project root:
GROQ_API_KEY=your_groq_api_key

CHROMA_DB_PATH=./chroma_store

SIMILARITY_THRESHOLD=0.80

GROQ_MODEL=llama-3.1-8b-instant

HF_HUB_DISABLE_SYMLINKS_WARNING=1
### 5. Ingest documents
Add your PDF files to the `data/` folder, then start the server and call:
```bash
uvicorn backend.main:app --reload
```
POST to `http://localhost:8000/ingest` with `{"source": "data/yourfile.pdf"}`

### 6. Open the chat UI
Open `test_chat.html` in your browser.

### 7. Open the agent dashboard
Open `agent_dashboard.html` in your browser.
Password: `vortexiq-agent-2026`

## Evaluation

The system achieves **100% pass rate** on a 15-query evaluation suite:
- 10 in-scope questions answered correctly
- 5 out-of-scope questions blocked with structured fallback
- 0% hallucination rate

## Project Structure
rag-support-agent/

├── backend/

│   ├── ingestion/

│   │   ├── loader.py      # PDF and web document loader

│   │   ├── chunker.py     # Text splitter

│   │   ├── embedder.py    # Sentence transformer embeddings

│   │   └── pipeline.py    # End-to-end ingestion pipeline

│   ├── vectordb/

│   │   └── store.py       # ChromaDB vector store

│   ├── rag/

│   │   ├── engine.py      # RAG engine with Groq LLM

│   │   └── fallback.py    # Out-of-scope fallback handler

│   ├── websocket/

│   │   └── sentiment.py   # VADER sentiment + escalation logic

│   └── main.py            # FastAPI app with all endpoints

├── data/                  # Knowledge base documents

├── logs/                  # Interaction logs (JSONL)

├── test_chat.html         # User chat interface

├── agent_dashboard.html   # Human agent dashboard

└── requirements.txt
## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Health check |
| POST | /ingest | Ingest a document |
| POST | /ask | Ask a question (REST) |
| GET | /sessions | List escalated sessions |
| POST | /agent-reply/{id} | Send agent reply |
| WS | /chat/{session_id} | Live WebSocket chat |

## Built by

Efro — AI Engineering Intern, VortexIQ  
GitHub: [Efrrowini](https://github.com/Efrrowini)