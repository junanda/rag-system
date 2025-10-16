# Fund Performance Analysis System - Coding Challenge

## Time Estimate: 1 Week (Senior Developer)

## Overview

Build an **AI-powered fund performance analysis system** that enables Limited Partners (LPs) to:
1. Upload fund performance PDF documents
2. Automatically parse and extract structured data (tables → SQL, text → Vector DB)
3. Ask natural language questions about fund metrics (DPI, IRR, etc.)
4. Get accurate answers powered by RAG (Retrieval Augmented Generation) and SQL calculations

---

## 🚀 Key Features

### 🧩 Document Intelligence
- Upload and parse PDF-based fund reports
- Extract and classify tables (Capital Calls, Distributions, Adjustments)
- Handle malformed PDFs gracefully
- Store structured data into PostgreSQL

### 🧩 AI-powered Analysis
- Ask natural language questions about fund metrics (DPI, IRR, etc.)
- Get accurate answers powered by RAG (Retrieval Augmented Generation) and SQL calculations

### 🔍 RAG-Powered Q&A
- Ask natural questions about fund performance  
  *(e.g., “What is the current DPI?”, “Show all distributions in 2024”)*
- Retrieve relevant context using **pgvector semantic search**
- Generate cited, contextual answers using **LLM (OpenAI or Ollama)**

### 📊 Metrics Computation
- Compute financial metrics including:
  - **DPI (Distributions to Paid-In)**
  - **IRR (Internal Rate of Return)**
  - **PIC (Paid-In Capital)**
- Provide detailed metric breakdowns
- Integrated validation and performance checks

### 💬 Conversational Chat
- Maintain multi-turn context (conversation history)
- Integrates RAG results and conversation memory
- Store chat logs in PostgreSQL (`conversation` & `message` tables)

### 🖥️ Web Dashboard
- View uploaded reports and extracted data
- Query insights visually
- Chat interface integrated with RAG pipeline
---

## 🧱 Tech Stack Overview

| Layer | Technology | Description |
|-------|-------------|--------------|
| **Frontend** | Next.js 14, TailwindCSS, shadcn/ui | Interactive web interface |
| **Backend** | FastAPI (Python 3.11) | API for parsing, chat, and metrics |
| **Database** | PostgreSQL + pgvector | Stores structured data and embeddings |
| **Worker** | Celery + Redis | Background document processing |
| **RAG System** | LangChain + OpenAI / Ollama | Context retrieval & LLM reasoning |
| **Containerization** | Docker + Compose | Fully isolated environment |

---

## ⚙️ Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- OpenAI API key (or use free alternatives - see below)

### Quick Start

**Clone the repository**
```bash
git clone <your-repo-url>
cd fpa-system
```


### 1️⃣ Environment Setup

Copy example config:

```bash
cp .env.example .env
```
Open file .env with your favorite editor:
```bash
nano .env
```
then edit .env file with your configuration:

```bash
# Database
DATABASE_URL=postgresql://funduser:fundpass@postgres:5432/funddb

# Redis docker
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# OpenAI (required for embeddings and LLM)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Use Ollama instead of OpenAI
# If you want use OpenAI change ollama with openai
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
---
## 🧠 Choosing the LLM

You can flexibly switch between OpenAI (cloud) and Ollama (local):

| Provider                     | Description                                           | When to Use                    |
| ---------------------------- | ----------------------------------------------------- | ------------------------------ |
| **OpenAI (ChatGPT / GPT-4)** | High accuracy, hosted API                             | Production or cloud usage      |
| **Ollama (Local LLM)**       | Runs locally via Ollama (e.g., Llama3, Mistral, Phi3) | Offline or secure environments |

✅ Example Ollama Setup

To use Ollama locally:

1. Install Ollama (https://ollama.com/)
2. Start Ollama server
3. Update .env with Ollama settings

## Install Ollama (Mac/Linux)
`curl -fsSL https://ollama.com/install.sh | sh`

## Pull a model (e.g., Llama3)
`ollama pull llama3`


✅ Example OpenAI Setup

To use OpenAI:

1. Get OpenAI API key (https://platform.openai.com/)
2. Update .env with OpenAI settings
---

## 🧰 Run with Docker
### 1️⃣ Build images (once)

backend
```bash
docker build -t fund-backend:latest ./backend
```
Frontend
```bash
docker build -t fund-frontend:latest ./frontend
```

## 2️⃣ Start services
```bash
docker-compose up -d
```
### This starts Container:

🗃️ PostgreSQL (with pgvector)

⚙️ Redis (for Celery tasks)

🧠 Backend (FastAPI)

💬 Frontend (Next.js)

🧾 Worker (Celery)

### 🌐 Access the App
| Service            | URL                                                      |
| ------------------ | -------------------------------------------------------- |
| Frontend UI        | [http://localhost:3000](http://localhost:3000)           |
| Backend API        | [http://localhost:8000](http://localhost:8000)           |
| API Docs (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |

## 🧩 Example Workflow

1. Upload PDF Report

   - Go to http://localhost:3000/upload

   - Upload example file: files/ILPA_Fund_Report.pdf

2. Automatic Extraction

   - Background worker parses the file and stores data

3. Ask a Question

   - Open Chat page: http://localhost:3000/chat

   - Example queries:

        - “What is the DPI for Fund A?”

        - “Show all capital calls in 2024”

        - “Explain what Paid-In Capital means”

---

## 🏗️ System Architecture

```bash
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

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- OpenAI API key (or use free alternatives - see below)

### Quick Start

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd fund-analysis-system
```

2. **Set up environment variables**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=sk-...
# DATABASE_URL=postgresql://user:password@localhost:5432/funddb
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

5. **Upload sample document**
- Navigate to http://localhost:3000/upload
- Upload the provided PDF: `files/ILPA based Capital Accounting and Performance Metrics_ PIC, Net PIC, DPI, IRR  .pdf`
- Wait for parsing to complete

6. **Start asking questions**
- Go to http://localhost:3000/chat
- Try: "What is DPI?"
- Try: "Calculate the current DPI for this fund"

---

## Project Structure

```bash
fund-analysis-system/
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
│   │   ├── upload/
│   │   │   └── page.tsx
│   │   ├── chat/
│   │   │   └── page.tsx
│   │   └── funds/
│   │       ├── page.tsx
│   │       └── [id]/
│   │           └── page.tsx
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
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

## API Endpoints

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

## ⚠️ Known Limitations
- Context window limited to last 6 messages (configurable)
- FlashRank reranking increases latency slightly
- LLM accuracy depends on model (OpenAI > Ollama)
- PDF parsing accuracy varies by document layout

## 🚧 Future Improvements
- Add multilingual support for document parsing
- Implement real-time streaming responses
- Add vector caching for repeated queries
- Improve reranking model fine-tuning

---
## 🖼️ Screenshots

### 1️⃣ Upload PDF Page
![Upload Page](docs/screenshots/upload_page.png)

### 2️⃣ Chat Interface (RAG QA)
![Chat Interface](docs/screenshots/chat_interface.png)

### 3️⃣ Funds Statistics
![Funds Statistics](docs/screenshots/funds_statistics.png)

---

## Fund Metrics Formulas

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
Uses numpy-financial.irr() function
```

See [CALCULATIONS.md](docs/CALCULATIONS.md) for detailed formulas.

---

## Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

### Test Document Upload
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@files/sample_fund_report.pdf"
```

### Test Chat Query
```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current DPI?",
    "fund_id": 1
  }'
```
---

## Troubleshooting

### Document Parsing Issues
**Problem**: Docling can't extract tables
**Solution**: 
- Check PDF format (ensure it's not scanned image)
- Add fallback parsing logic
- Manually define table structure patterns

### LLM API Costs
**Problem**: OpenAI API is expensive
**Solution**: Use free alternatives (see "Free LLM Options" section below)
- Use caching for repeated queries
- Use cheaper models (gpt-3.5-turbo)
- Use local LLM (Ollama) for development

### IRR Calculation Errors
**Problem**: IRR returns NaN or extreme values
**Solution**:
- Validate cash flow sequence
- Check for missing dates
- Handle edge cases (all positive/negative flows)

### CORS Issues
**Problem**: Frontend can't call backend API
**Solution**:
- Add CORS middleware in FastAPI
- Allow origin: http://localhost:3000
- Check network configuration in Docker

---

## Free LLM Options

You don't need to pay for OpenAI API! Here are free alternatives:

### Option 1: Ollama (Recommended for Development)

**Completely free, runs locally on your machine**

1. **Install Ollama**
```bash
# Mac
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

2. **Download a model**
```bash
# Llama 3.2 (3B - fast, good for development)
ollama pull llama3.2

# Or Llama 3.1 (8B - better quality)
ollama pull llama3.1

# Or Mistral (7B - good balance)
ollama pull mistral
```

3. **Update your .env**
```bash
# Use Ollama instead of OpenAI
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

4. **Modify your code to use Ollama**
```python
# In backend/app/services/query_engine.py
from langchain_community.llms import Ollama

llm = Ollama(
    base_url="http://localhost:11434",
    model="llama3.2"
)
```

**Pros**: Free, private, no API limits, works offline
**Cons**: Requires decent hardware (8GB+ RAM), slower than cloud APIs

---

### Option 2: Google Gemini (Free Tier)

**Free tier: 60 requests per minute**

1. **Get free API key**
   - Go to https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy your key

2. **Install package**
```bash
pip install langchain-google-genai
```

3. **Update .env**
```bash
GOOGLE_API_KEY=your-gemini-api-key
LLM_PROVIDER=gemini
```

4. **Use in code**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

**Pros**: Free, fast, good quality
**Cons**: Rate limits, requires internet

---

### Option 3: Groq (Free Tier)

**Free tier: Very fast inference, generous limits**

1. **Get free API key**
   - Go to https://console.groq.com
   - Sign up and get API key

2. **Install package**
```bash
pip install langchain-groq
```

3. **Update .env**
```bash
GROQ_API_KEY=your-groq-api-key
LLM_PROVIDER=groq
```

4. **Use in code**
```python
from langchain_groq import ChatGroq

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="mixtral-8x7b-32768"  # or "llama3-70b-8192"
)
```

**Pros**: Free, extremely fast, good quality
**Cons**: Rate limits, requires internet

---

### Option 4: Hugging Face (Free)

**Free inference API**

1. **Get free token**
   - Go to https://huggingface.co/settings/tokens
   - Create a token

2. **Update .env**
```bash
HUGGINGFACE_API_TOKEN=your-hf-token
LLM_PROVIDER=huggingface
```

3. **Use in code**
```python
from langchain_community.llms import HuggingFaceHub

llm = HuggingFaceHub(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN")
)
```

**Pros**: Free, many models available
**Cons**: Can be slow, rate limits

---

### Comparison Table

| Provider | Cost | Speed | Quality | Setup Difficulty |
|----------|------|-------|---------|------------------|
| **Ollama** | Free | Medium | Good | Easy |
| **Gemini** | Free | Fast | Very Good | Very Easy |
| **Groq** | Free | Very Fast | Good | Very Easy |
| **Hugging Face** | Free | Slow | Varies | Easy |
| OpenAI | Paid | Fast | Excellent | Very Easy |

### Recommended Setup for This Project

**For Development/Testing:**
- Use **Ollama** with `llama3.2` (free, no limits)

**For Production/Demo:**
- Use **Groq** or **Gemini** (free tier is generous)

**If you have budget:**
- Use **OpenAI GPT-4** (best quality)

---

## Sample Data

### Provided Sample Files

Located in `files/` directory:

1. **`ILPA based Capital Accounting and Performance Metrics_ PIC, Net PIC, DPI, IRR.pdf`**
   - Reference document explaining fund metrics
   - Contains definitions of PIC, DPI, IRR, TVPI
   - Use this to test text extraction and RAG

### Sample Data You Should Create

For comprehensive testing, you should create **mock fund performance reports** with:

#### Example Capital Call Table
```
Date       | Call Number | Amount      | Description
-----------|-------------|-------------|------------------
2023-01-15 | Call 1      | $5,000,000  | Initial Capital
2023-06-20 | Call 2      | $3,000,000  | Follow-on
2024-03-10 | Call 3      | $2,000,000  | Bridge Round
```

#### Example Distribution Table
```
Date       | Type        | Amount      | Recallable | Description
-----------|-------------|-------------|------------|------------------
2023-12-15 | Return      | $1,500,000  | No         | Exit: Company A
2024-06-20 | Income      | $500,000    | No         | Dividend
2024-09-10 | Return      | $2,000,000  | Yes        | Partial Exit: Company B
```

#### Example Adjustment Table
```
Date       | Type                | Amount    | Description
-----------|---------------------|-----------|------------------
2024-01-15 | Recallable Dist     | -$500,000 | Recalled distribution
2024-03-20 | Capital Call Adj    | $100,000  | Fee adjustment
```

### Expected Test Results

For the sample data above:
- **Total Capital Called**: $10,000,000
- **Total Distributions**: $4,000,000
- **Net PIC**: $10,100,000 (after adjustments)
- **DPI**: 0.40 (4M / 10M)
- **IRR**: ~8-12% (depends on exact dates)

### Creating Test PDFs

#### Option 1: Use Provided Script (Recommended)

We've included a Python script to generate sample PDFs:

```bash
cd files/
pip install reportlab
python create_sample_pdf.py
```

This creates `Sample_Fund_Performance_Report.pdf` with:
- Capital calls table (4 entries)
- Distributions table (4 entries)
- Adjustments table (3 entries)
- Performance summary with definitions

#### Option 2: Create Your Own

You can create PDFs using:
- Google Docs/Word → Export as PDF
- Python libraries (reportlab, fpdf)
- Online PDF generators

**Tip**: Start with simple, well-structured tables before handling complex layouts.

---

## Reference Materials

- **Docling**: https://github.com/DS4SD/docling
- **LangChain RAG**: https://python.langchain.com/docs/use_cases/question_answering/
- **FAISS**: https://faiss.ai/
- **ILPA Guidelines**: https://ilpa.org/
- **PE Metrics**: https://www.investopedia.com/terms/d/dpi.asp

---