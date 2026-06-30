# Fund Performance Analysis (FP&A) System

An **AI-powered fund performance analysis system** that lets Limited Partners (LPs) upload fund
performance PDF reports, automatically extract structured data, and ask natural-language questions
about fund metrics (DPI, IRR, PIC, etc.) — answered through a combination of **RAG (Retrieval
Augmented Generation)** and **SQL-based metric calculations**.

> **Project background**
> This project started from an InterOpera take-home assignment and has since been continued and
> extended as a **personal project** for learning and experimentation. The original assignment
> brief is no longer reflected here — this README documents the project as it stands now.

---

## ✨ What it does

1. Upload fund performance PDF documents
2. Automatically parse and extract structured data (tables → SQL, text → vector DB)
3. Ask natural-language questions about fund metrics
4. Get accurate, cited answers powered by RAG and SQL computations

---

## 🚀 Key Features

### 🧩 Document Intelligence
- Upload and parse PDF-based fund reports
- Extract and classify tables (Capital Calls, Distributions, Adjustments)
- Handle malformed PDFs gracefully
- Store structured data into PostgreSQL

### 🔍 RAG-Powered Q&A
- Ask natural questions about fund performance
  *(e.g. “What is the current DPI?”, “Show all distributions in 2024”)*
- Retrieve relevant context using **pgvector semantic search**
- Generate cited, contextual answers using an **LLM (OpenAI or Ollama)**

### 📊 Metrics Computation
- Compute financial metrics including:
  - **DPI** (Distributions to Paid-In)
  - **IRR** (Internal Rate of Return)
  - **PIC** (Paid-In Capital)
- Provide detailed metric breakdowns with validation checks

### 💬 Conversational Chat
- Maintain multi-turn context (conversation history)
- Combine RAG results with conversation memory
- Persist chat logs in PostgreSQL (`conversation` & `message` tables)

### 🖥️ Web Dashboard
- View uploaded reports and extracted data
- Query insights visually
- Chat interface integrated with the RAG pipeline

---

## 🧱 Tech Stack

| Layer | Technology | Description |
|-------|-------------|--------------|
| **Frontend** | Next.js 14, TailwindCSS, shadcn/ui | Interactive web interface |
| **Backend** | FastAPI (Python 3.11) | API for parsing, chat, and metrics |
| **Database** | PostgreSQL + pgvector | Structured data and embeddings |
| **Worker** | Celery + Redis | Background document processing |
| **RAG** | LangChain + OpenAI / Ollama | Context retrieval & LLM reasoning |
| **Containerization** | Docker + Compose | Fully isolated environment |

---

## ⚙️ Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- An OpenAI API key *(optional — you can run fully locally with Ollama)*

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd fpa-system
```

### 2. Configure environment
```bash
cp .env.example .env
```
Then edit `.env` with your configuration:

```bash
# Database
DATABASE_URL=postgresql://funduser:fundpass@postgres:5432/funddb

# Redis (Docker)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# OpenAI (used for embeddings and LLM when LLM_PROVIDER=openai)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM provider — set to "openai" or "ollama"
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Rerank using flashrank
FLASHRANK_MODEL=ms-marco-MiniLM-L-12-v2

# Anthropic (optional)
ANTHROPIC_API_KEY=

# Application
PROJECT_NAME=Fund Performance Analysis System
VERSION=1.0.0

# File Upload
UPLOAD_DIR=./app/uploads
MAX_UPLOAD_SIZE=52428800

# Vector Store
VECTOR_STORE_PATH=./app/vector_store
FAISS_INDEX_PATH=./app/faiss_index

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# RAG
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
```

### 3. Run with Docker Compose
```bash
docker-compose up -d
```

This starts the following containers:

- 🗃️ PostgreSQL (with pgvector)
- ⚙️ Redis (for Celery tasks)
- 🧠 Backend (FastAPI)
- 💬 Frontend (Next.js)
- 🧾 Worker (Celery)

> To build the images manually:
> ```bash
> docker build -t fund-backend:latest ./backend
> docker build -t fund-frontend:latest ./frontend
> ```

### 4. Access the app
| Service            | URL                                                      |
| ------------------ | -------------------------------------------------------- |
| Frontend UI        | [http://localhost:3000](http://localhost:3000)           |
| Backend API        | [http://localhost:8000](http://localhost:8000)           |
| API Docs (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

## 🧠 Choosing the LLM

You can switch between OpenAI (cloud) and Ollama (local) via the `LLM_PROVIDER` env var:

| Provider | Description | When to Use |
| -------- | ----------- | ----------- |
| **OpenAI (GPT-4)** | High accuracy, hosted API | Production or cloud usage |
| **Ollama (Local LLM)** | Runs locally (Llama3, Mistral, Phi3, …) | Offline or secure environments |

**Use Ollama locally**
```bash
# Install Ollama (Mac/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2
```
Then set `LLM_PROVIDER=ollama` in `.env`.

**Use OpenAI**
1. Get an API key at https://platform.openai.com/
2. Set `LLM_PROVIDER=openai` and `OPENAI_API_KEY=...` in `.env`

---

## 🧩 Example Workflow

1. **Upload a PDF report** — go to http://localhost:3000/upload and upload a fund report
   (e.g. `files/ILPA_Fund_Report.pdf`).
2. **Automatic extraction** — a background worker parses the file and stores the data.
3. **Ask a question** — open http://localhost:3000/chat and try:
   - “What is the DPI for Fund A?”
   - “Show all capital calls in 2024”
   - “Explain what Paid-In Capital means”

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Upload     │  │     Chat     │  │   Dashboard  │       │
│  │     Page     │  │  Interface   │  │     Page     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Document Processor                     │    │
│  │  ┌──────────────┐         ┌──────────────┐          │    │
│  │  │   Docling    │────────▶│  Table       │          │    │
│  │  │   Parser     │         │  Extractor   │          │    │
│  │  └──────────────┘         └──────┬───────┘          │    │
│  │                                   │                 │    │
│  │  ┌──────────────┐         ┌──────▼───────┐          │    │
│  │  │   Text       │────────▶│  Embedding   │          │    │
│  │  │   Chunker    │         │  Generator   │          │    │
│  │  └──────────────┘         └──────────────┘          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Query Engine (RAG)                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐   │    │
│  │  │   Intent     │─▶│   Vector     │─▶│   LLM    │   │    │
│  │  │  Classifier  │  │   Search     │  │ Response │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────┘   │    │
│  │                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐                 │    │
│  │  │  Metrics     │─▶│     SQL      │                 │    │
│  │  │ Calculator   │  │   Queries    │                 │    │
│  │  └──────────────┘  └──────────────┘                 │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼─────┐ ┌────────▼────────┐
│   PostgreSQL   │ │  PgVector│ │     Redis       │
│  (Structured)  │ │ (Vectors)│ │  (Task Queue)   │
└────────────────┘ └──────────┘ └─────────────────┘
```

---

## 📁 Project Structure

```text
fpa-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── documents.py
│   │   │   │   ├── funds.py
│   │   │   │   ├── chat.py
│   │   │   │   └── metrics.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   ├── models/
│   │   │   ├── fund.py
│   │   │   ├── transaction.py
│   │   │   └── document.py
│   │   ├── schemas/
│   │   │   ├── fund.py
│   │   │   ├── transaction.py
│   │   │   ├── conversation.py
│   │   │   ├── document.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── document_processor.py
│   │   │   ├── table_parser.py
│   │   │   ├── vector_store.py
│   │   │   ├── query_engine.py
│   │   │   └── metrics_calculator.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_document_processor.py
│   │   ├── test_metrics.py
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/
│       └── versions/
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── upload/page.tsx
│   │   ├── chat/page.tsx
│   │   └── funds/
│   │       ├── page.tsx
│   │       └── [id]/page.tsx
│   ├── components/
│   │   ├── ui/
│   │   ├── FileUpload.tsx
│   │   ├── ChatInterface.tsx
│   │   ├── FundMetrics.tsx
│   │   └── TransactionTable.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── docs/
    ├── API.md
    ├── ARCHITECTURE.md
    └── CALCULATIONS.md
```

---

## 🔌 API Endpoints

### Documents
```
POST   /api/documents/upload
GET    /api/documents/{doc_id}/status
GET    /api/documents/{doc_id}
DELETE /api/documents/{doc_id}
```

### Funds
```
GET    /api/funds
POST   /api/funds
GET    /api/funds/{fund_id}
GET    /api/funds/{fund_id}/transactions
GET    /api/funds/{fund_id}/metrics
```

### Chat
```
POST   /api/chat/query
GET    /api/chat/conversations/{conv_id}
POST   /api/chat/conversations
```

See [API.md](docs/API.md) for detailed documentation.

---

## 📐 Fund Metrics Formulas

### Paid-In Capital (PIC)
```
PIC = Total Capital Calls - Adjustments
```

### DPI (Distribution to Paid-In)
```
DPI = Cumulative Distributions / PIC
```

### IRR (Internal Rate of Return)
```
IRR = Rate where NPV of all cash flows = 0
Uses numpy-financial.irr()
```

See [CALCULATIONS.md](docs/CALCULATIONS.md) for detailed formulas.

---

## 🧪 Testing

**Backend**
```bash
cd backend
pytest tests/ -v --cov=app
```

**Frontend**
```bash
cd frontend
npm test
```

**Test document upload**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@files/sample_fund_report.pdf"
```

**Test chat query**
```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the current DPI?", "fund_id": 1}'
```

---

## 📦 Sample Data

A reference document is provided under `files/`:

- **`ILPA based Capital Accounting and Performance Metrics_ PIC, Net PIC, DPI, IRR.pdf`**
  — explains fund metrics (PIC, DPI, IRR, TVPI). Useful for testing text extraction and RAG.

You can also generate a synthetic fund report with the included script:

```bash
cd files/
pip install reportlab
python create_sample_pdf.py
```

This produces `Sample_Fund_Performance_Report.pdf` containing capital calls, distributions,
adjustments, and a performance summary.

**Example expected results** for the generated sample data:

| Metric | Value |
| ------ | ----- |
| Total Capital Called | $10,000,000 |
| Total Distributions | $4,000,000 |
| Net PIC (after adjustments) | $10,100,000 |
| DPI | 0.40 |
| IRR | ~8–12% (depends on exact dates) |

---

## 🖼️ Screenshots

### Upload PDF Page
![Upload Page](docs/screenshots/upload_page.png)

### Chat Interface (RAG QA)
![Chat Interface](docs/screenshots/chat_interface.png)

### Funds Statistics
![Funds Statistics](docs/screenshots/funds_statistics.png)

---

## ⚠️ Known Limitations
- Context window limited to the last 6 messages (configurable)
- FlashRank reranking adds slight latency
- LLM accuracy depends on the model (OpenAI > Ollama)
- PDF parsing accuracy varies by document layout

## 🚧 Future Improvements
- Multilingual support for document parsing
- Real-time streaming responses
- Vector caching for repeated queries
- Reranking model fine-tuning

---

## 🛠️ Troubleshooting

**Docling can't extract tables**
- Ensure the PDF is not a scanned image
- Add fallback parsing logic / define table structure patterns

**IRR returns NaN or extreme values**
- Validate the cash-flow sequence and dates
- Handle edge cases (all-positive / all-negative flows)

**Frontend can't call the backend (CORS)**
- Ensure CORS middleware allows `http://localhost:3000`
- Check the Docker network configuration

**LLM API costs too high**
- Use a local LLM (Ollama) for development
- Use cheaper models and cache repeated queries

---

## 📚 Reference Materials

- **Docling**: https://github.com/DS4SD/docling
- **LangChain RAG**: https://python.langchain.com/docs/use_cases/question_answering/
- **FAISS**: https://faiss.ai/
- **ILPA Guidelines**: https://ilpa.org/
- **PE Metrics**: https://www.investopedia.com/terms/d/dpi.asp

---

## 📄 License & Attribution

This is a personal project, originally bootstrapped from an InterOpera take-home assignment and
since developed independently for learning purposes.
</content>
</invoke>
