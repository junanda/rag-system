FROM python:3.12-slim as base

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install system dependencies in one layer and clean up immediately
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements
COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Set environment variables for HuggingFace
ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface/transformers
ENV SENTENCE_TRANSFORMERS_HOME=/root/.cache/huggingface/sentence-transformers
ENV EASYOCR_MODULE_PATH=/root/.EasyOCR
ENV FLASHRANK_CACHE=/root/.cache/flashrank

# === Pre-download models during build ===
# Add build arguments for dynamic model names
ARG SENTENCE_MODEL=sentence-transformers/all-MiniLM-L6-v2
ARG HUGGINGFACE_MODEL=sentence-transformers/all-MiniLM-L6-v2
ARG EASYOCR_MODEL=en
ARG FLASHRANK_MODEL=ms-marco-MiniLM-L-12-v2

# Export build args to environment for subsequent RUN steps
ENV SENTENCE_MODEL=${SENTENCE_MODEL}
ENV HUGGINGFACE_MODEL=${HUGGINGFACE_MODEL}
ENV EASYOCR_MODEL=${EASYOCR_MODEL}
ENV FLASHRANK_MODEL=${FLASHRANK_MODEL}

# Download SentenceTransformer model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${SENTENCE_MODEL}')"

# Download HuggingFace embedding model
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='${HUGGINGFACE_MODEL}')"

# Download FlashRank model
RUN python - <<PY
import os
from flashrank import Ranker
model = Ranker(model_name=os.environ.get("FLASHRANK_MODEL", "ms-marco-MiniLM-L-12-v2"))
print("✅ FlashRank model downloaded and cached.")
PY

# === Pre-download EasyOCR models ===
RUN python - <<PY
import os
import easyocr
lang = os.environ.get("EASYOCR_MODEL", "en")
reader = easyocr.Reader([lang])
print("✅ EasyOCR models downloaded and cached.")
PY

# Copy application code
COPY . .

# Recognition package app for Python
ENV PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p /app/uploads /app/vector_store /app/faiss_index

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
