"""
Query engine service for RAG-based question answering
"""
from fastapi import Depends
from typing import Dict, Any, List, Optional
import time
from app.core.config import settings
from app.services.vector_store import VectorStore, get_vector_store_service
from app.services.metrics_calculator import MetricsCalculator, get_metrics_calculator_service
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.rag_service import RAGService, get_rag_service

def get_query_engine_service(
    db: Session = Depends(get_db), 
    rag_service: RAGService = Depends(get_rag_service),
    vector_store: VectorStore = Depends(get_vector_store_service),
    metrics_calculator: MetricsCalculator = Depends(get_metrics_calculator_service)
    ):
    return QueryEngine(db, rag_service, vector_store, metrics_calculator)

class QueryEngine:
    """RAG-based query engine for fund analysis"""
    
    def __init__(self, db: Session, rag_service: RAGService, vector_store: VectorStore, metrics_calculator: MetricsCalculator):
        self.db = db
        self.rag_service = rag_service
        self.vector_store = vector_store
        self.metrics_calculator = metrics_calculator
    
    async def process_query(
        self, 
        query: str, 
        fund_id: Optional[int] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query using RAG
        
        Args:
            query: User question
            fund_id: Optional fund ID for context
            conversation_history: Previous conversation messages
            
        Returns:
            Response with answer, sources, and metrics
        """
        start_time = time.time()
        
        # Step 1: Classify query intent
        intent = await self._classify_intent(query)
        
        # Step 2: Calculate metrics if needed
        metrics = None
        if intent == "calculation" and fund_id:
            metrics = self.metrics_calculator.calculate_all_metrics(fund_id)

        # Step 3: Run RAG
        rag_result = await self.rag_service.run(
            query=query,
            fund_id=fund_id,
            conversation_history=conversation_history or [],
            top_k_retrieve=settings.TOP_K_RESULTS,
            metrics=metrics
        )
        
        processing_time = time.time() - start_time
        
        return {
            "answer": rag_result["answer"],
            "sources": [
                {
                    "content": doc["content"],
                    "metadata": {
                        k: v for k, v in doc.items() 
                        if k not in ["content", "score"]
                    },
                    "score": doc.get("score")
                }
                for doc in rag_result["reranked_docs"]
            ],
            "metrics": metrics,
            "processing_time": round(processing_time, 2)
        }
    
    async def _classify_intent(self, query: str) -> str:
        """
        Classify query intent
        
        Returns:
            'calculation', 'definition', 'retrieval', or 'general'
        """
        query_lower = query.lower()
        
        # Calculation keywords
        calc_keywords = [
            "calculate", "what is the", "current", "dpi", "irr", "tvpi", 
            "rvpi", "pic", "paid-in capital", "return", "performance"
        ]
        if any(keyword in query_lower for keyword in calc_keywords):
            return "calculation"
        
        # Definition keywords
        def_keywords = [
            "what does", "mean", "define", "explain", "definition", 
            "what is a", "what are"
        ]
        if any(keyword in query_lower for keyword in def_keywords):
            return "definition"
        
        # Retrieval keywords
        ret_keywords = [
            "show me", "list", "all", "find", "search", "when", 
            "how many", "which"
        ]
        if any(keyword in query_lower for keyword in ret_keywords):
            return "retrieval"
        
        return "general"
