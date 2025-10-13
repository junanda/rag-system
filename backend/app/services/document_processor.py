"""
Document processing service using pdfplumber

TODO: Implement the document processing pipeline
- Extract tables from PDF using pdfplumber
- Classify tables (capital calls, distributions, adjustments)
- Extract and chunk text for vector storage
- Handle errors and edge cases
"""
from typing import Dict, List, Any
# from langchain_experimental.text_splitter import SemanticChunker
# from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from docling.document_converter import DocumentConverter
from sklearn.metrics.pairwise import cosine_similarity
from app.services.vector_store import VectorStore
from app.core.config import settings
from app.services.table_parser_v2 import TableParser
from app.services.markdown_cleaner import MarkdownCleaner
from app.services.table_converter import TableToParagraphConverter
from app.services.markdown_table_replacement import MarkdownTableReplacer
from app.repository.document_repository import DocumentRepository
from app.repository.capitalcall_repository import CapitalCallRepository
from app.repository.distribution_repository import DistributionRepository
from app.repository.adjustment_repository import AdjustmentRepository
import pdfplumber
import logging
import re
import numpy as np
import spacy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process PDF documents and extract structured data"""
    
    def __init__(self):
        self.table_parser = TableParser()
        self.vector_store = VectorStore()
        self.embedding_model = SentenceTransformer()
        self.markdown_cleaner = MarkdownCleaner()
        self.converter = DocumentConverter()
        self.table_converter = TableToParagraphConverter()
        self.table_replacer = MarkdownTableReplacer()
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.doc_repo = DocumentRepository()
        self.capitalcall_repo = CapitalCallRepository()
        self.distribution_repo = DistributionRepository()
        self.adjustment_repo = AdjustmentRepository()
        self.stats = {
            "pages_processed": 0,
            "tables_extracted": 0,
            "chunks_embedded_and_stored": 0,
            "errors": []
        }
        self._initiliaze_embeddings()
    
    def _initiliaze_embeddings(self):
        # self.embedding_model = HuggingFaceEmbeddings(
        #     model_name=settings.EMBEDDING_MODEL,
        #     model_kwargs={
        #         "device": "cpu"
        #     },
        #     encode_kwargs={
        #         "normalize_embeddings": True
        #     }
        # )
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.NLP = spacy.load("en_core_web_sm")
    
    async def process_document(self, file_path: str, document_id: int, fund_id: int) -> Dict[str, Any]:
        """
        Process a PDF document
        
        TODO: Implement this method
        - Open PDF with pdfplumber
        - Extract tables from each page
        - Parse and classify tables using TableParser
        - Extract text and create chunks
        - Store chunks in vector database
        - Return processing statistics
        
        Args:
            file_path: Path to the PDF file
            document_id: Database document ID
            fund_id: Fund ID
            
        Returns:
            Processing result with statistics
        """
        try:
            logger.info(f"Converting {file_path} with Docling...")
            conv_res = self.converter.convert(file_path)
            doc = conv_res.document
        
            full_text = doc.export_to_markdown()
            self.stats["pages_processed"] = doc.page_count if hasattr(doc, "page_count") else 1

            all_tables = self.table_parser.table_classification(doc, self.stats)
            
            self.capitalcall_repo.create_bulk(fund_id, all_tables.get("capital_calls"))
            self.distribution_repo.create_bulk(fund_id, all_tables.get("distributions"))
            self.adjustment_repo.create_bulk(fund_id, all_tables.get("adjustments"))

            table_paragraphs = self.table_converter.convert_tables_to_paragraphs(all_tables)
            
            clean_text = self.markdown_cleaner.clean_markdown_text(full_text)
            clean_text = self.table_replacer.replace_tables_with_paragraphs(clean_text, table_paragraphs)
            
            chunk_inputs = [{"text": clean_text, "source": file_path, "document_id": document_id, "fund_id": fund_id}]
    
            chunks = self._chunk_text(chunk_inputs)

            # 4. Embed and store each chunk
            for content in chunks:
                await self.vector_store.add_document(content.get('text'), content.get('metadata'))
                self.stats["chunks_embedded_and_stored"] += 1
            
            # update status doc to finish
            # self.doc_repo.update_status(document_id, "completed")
            
            # 5. Ekstrak metadata kunci
            performance = self._extract_performance(full_text)
            fund_strategy = self._extract_fund_strategy(full_text)

            return {
                "tables": all_tables,
                "performance_summary": performance,
                "fund_strategy": fund_strategy,
                "statistics": self.stats,
                "status": "completed"
            }
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.stats["errors"].append(str(e))
            return {
                "tables": {"capital_calls": [], "distributions": [], "adjustments": []},
                "performance_summary": {},
                "fund_strategy": "",
                "statistics": self.stats,
                "status": "failed"
            }
        # finally:
        #     self.vector_store.close()
    
    def _chunk_text(self, text_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk text content for vector storage
        
        TODO: Implement intelligent text chunking
        - Split text into semantic chunks
        - Maintain context overlap
        - Preserve sentence boundaries
        - Add metadata to each chunk
        
        Args:
            text_content: List of text content with metadata
            
        Returns:
            List of text chunks with metadata
        """
        logger.info("Menggunakan model embedding gratis: all-MiniLM-L6-v2...")

        all_chunks = []
        for item in text_content:
            raw_text = item.get("text", "").strip()
            if not raw_text:
                continue

            # source = item.get("source", "unknown")
            base_metadata = {k: v for k, v in item.items() if k != "text"}
            
            # Extract sentences using spaCy and convert to strings
            doc = self.NLP(raw_text)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

            if not sentences:
                continue

            # Encode sentences as embeddings
            embeddings = self.model.encode(sentences, convert_to_tensor=False)

            distance = []
            for i in range(len(embeddings)-1):
                sim = cosine_similarity(embeddings[i].reshape(1, -1), embeddings[i+1].reshape(1, -1))[0][0]
                distance.append(1 - sim)

            threshold = np.mean(distance) + np.std(distance) * 0.5
            logging.info(f"Ambang batas jarak Kosinus (Distance Treshold): {threshold:.4f}")

            current_chunk = []
            current_len = 0
            chunk_index = 0

            for i, sent in enumerate(sentences):
                sent_len = len(sent)

                if current_len + sent_len > self.chunk_size and current_chunk:
                    # Finalize current chunk
                    chunk_text = " ".join(current_chunk).strip()
                    all_chunks.append({
                        "text": chunk_text,
                        "embedding": None,
                        "metadata": {
                            **base_metadata,
                            "chunk_index": chunk_index,
                            "char_start": sum(len(s) + 1 for s in sentences[:i - len(current_chunk)]),
                            "char_end": sum(len(s) + 1 for s in sentences[:i]),
                        }
                    })
                    chunk_index += 1

                    # Apply overlap: keep trailing sentences within overlap limit
                    overlap_chars = 0
                    overlap_sentences = []
                    for s in reversed(current_chunk):
                        if overlap_chars + len(s) <= self.chunk_overlap:
                            overlap_sentences.insert(0, s)
                            overlap_chars += len(s) + 1
                        else:
                            break

                    current_chunk = overlap_sentences
                    current_len = overlap_chars

                current_chunk.append(sent)
                current_len += sent_len + 1  # +1 for space
            
            # Final chunk
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                all_chunks.append({
                    "text": chunk_text,
                    "embedding": None,
                    "metadata": {
                        **base_metadata,
                        "chunk_index": chunk_index,
                        "char_start": sum(len(s) + 1 for s in sentences[:-len(current_chunk)]),
                        "char_end": sum(len(s) + 1 for s in sentences),
                    }
                })

        return all_chunks

    def _extract_performance(self, text: str) -> Dict[str, Any]:
        metrics = {}
        patterns = {
            "total_capital_called": r"Total Capital Called:\s*\$(\d{1,3}(?:,\d{3})*)",
            "total_distributions": r"Total Distributions:\s*\$(\d{1,3}(?:,\d{3})*)",
            "net_pic": r"Net Paid-In Capital\(PIC\):\s*\$(\d{1,3}(?:,\d{3})*)",
            "dpi": r"DPI.*?:\s*([\d.]+)",
            "irr": r"IRR.*?:\s*([\d.]+)%?",
            "tvpi": r"TVPI.*?:\s*([\d.]+)"
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                val = match.group(1).replace(",", "")
                metrics[key] = float(val) if "." in val or key in ["dpi", "irr", "tvpi"] else int(val)
        return metrics
    
    def _extract_fund_strategy(self, text: str) -> str:
        match = re.search(r"Fund Strategy:\s*(.+?)(?:\n\n|Key Definitions:|$)", text, re.DOTALL)
        return match.group(1).strip() if match else ""


if __name__ == '__main__':
    import asyncio

    processor = DocumentProcessor()
    result = asyncio.run(processor.process_document("../files/Sample_Fund_Performance_Report.pdf", 1, 1))

    print("✅ Fund Strategy:", result["fund_strategy"])
    print("📊 IRR:", result["performance_summary"].get("irr"), "%")
    print("📈 Capital Calls:", len(result["tables"]["capital_calls"]), "entries")
    print("📦 Chunks stored:", result["statistics"]["chunks_embedded_and_stored"])
