
from app.services.vector_store import VectorStore
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from flashrank import Ranker, RerankRequest
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings
from typing import List, Dict, Any, Optional
import asyncio

def get_rag_service(db: Session = Depends(get_db)):
    return RAGService(db, VectorStore())

class RAGService:

    def __init__(self, db: Session, vector_store: VectorStore):
        self.db = db
        self.vector_store = vector_store
        self.llm = self._initialize_llm()
        self.ranker = Ranker(model_name=settings.FLASHRANK_MODEL)

    def _initialize_llm(self):
        if settings.LLM_PROVIDER == "openai":
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            # Fallback to local LLM
            return Ollama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL
            )
    
    async def run(
        self,
        query: str,
        fund_id: Optional[int] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k_retrieve: int = 5,
        top_k_rerank: int = 5,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
            Full RAG run:
            1. Retrieve from vector store
            2. Rerank with FlashRank
            3. Build prompt + call LLM
            4. Return answer + sources + docs
        """
        filter_metadata = {"fund_id": fund_id} if fund_id is not None else None

        # 1. Retrieve
        retrieved_docs = await self.retrieve(query=query, k=top_k_retrieve, filter_metadata=filter_metadata)

        # 2. Rerank using FlashRank
        reranked_docs = await self.rerank(query=query, docs=retrieved_docs, top_k=top_k_rerank)

        # 3. Build prompt
        prompt = await self._build_prompt(query=query, reranked_docs=reranked_docs, conversation_history=conversation_history, metrics=metrics)

        # 4. Generate answer
        answer = await self.generate(prompt)

        # 5. Prepare sources for return
        sources = []
        for i, d in enumerate(reranked_docs):
            sources.append({
                "source": f"Source {i+1}",
                "id": str(d.get("id")),
                "score": d.get("rerank_score", d.get("score")),
                "metadata": d.get("metadata"),
                "content_snippet": (d.get("content") or "")[:500]
            })

        return {
            "answer": answer,
            "retrieved_docs": retrieved_docs,
            "reranked_docs": reranked_docs,
            "sources": sources,
            "metrics": metrics
        }
    
    async def retrieve(
        self, 
        query: str, 
        k: int = 5, 
        filter_metadata: Optional[Dict[str, Any]] = None
        ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k documents from VectorStore (pgvector).
        Returns list of dict: {"id","content","metadata","score"}
        """
        if asyncio.iscoroutinefunction(self.vector_store.similarity_search):
            docs = await self.vector_store.similarity_search(query=query, k=k, filter_metadata=filter_metadata)
        else:
            docs = await asyncio.to_thread(self.vector_store.similarity_search, query, k, filter_metadata)
        return docs
    
    async def rerank(self, query: str, docs: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank docs using FlashRank. FlashRank Ranker API expects a RerankRequest or similar.
        We'll offload to thread since FlashRank is CPU-bound / sync.
        Returned docs keep original fields + 'rerank_score' (higher = better).
        """
        if not docs:
            return []
        
        passages = [{"id": str(d["id"]), "text": d.get("content", "")} for d in docs]

        def _sync_rerank(query_text: str, passages_list: List[Dict[str, Any]]):
            req = RerankRequest(
                query=query_text,
                passages=passages_list
            )
            resp = self.ranker.rerank(req)
            
            score_map = {}
            for r in resp:
                doc_id = r["id"]
                score_map[doc_id] = float(r["score"])
            
            reranked = []
            for d in docs:
                doc_id = str(d["id"])
                d_copy = d.copy()
                d_copy["rerank_score"] = score_map.get(doc_id, 0.0)
                reranked.append(d_copy)
            # sort by rerank_score desc
            reranked_sorted = sorted(reranked, key=lambda x: x["rerank_score"], reverse=True)
            return reranked_sorted[:top_k]
        reranked_docs = await asyncio.to_thread(_sync_rerank, query, passages)
        return reranked_docs
    
    async def _build_prompt(self, query: str, reranked_docs: List[Dict[str, Any]], conversation_history: Optional[List[Dict[str, str]]] = None, metrics: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Build prompt text (string) to send to the LLM.
        Keep prompt compact: include most relevant docs (top 3) and last few conversation messages.
        """
        history_str = ""
        if conversation_history:
            last_message = conversation_history[-6:]
            lines = []
            for msg in last_message:
                # Support both ORM objects and plain dicts
                role = getattr(msg, "role", None) if not isinstance(msg, dict) else msg.get("role")
                content = getattr(msg, "content", None) if not isinstance(msg, dict) else msg.get("content")
                if not role or content is None:
                    continue
                if role.lower() == "user":
                    lines.append(f"User: {content}")
                else:
                    lines.append(f"Assistant: {content}")
            history_str = "\n".join(lines)
        
        # top doc contexts
        context_parts = []
        for i, doc in enumerate(reranked_docs[:5]):
            meta = doc.get("metadata") or {}
            header = f"[Source {i+1}]"
            if meta:
                # include short metadata summary useful for citation
                header += " " + ", ".join(f"{k}={v}" for k, v in (list(meta.items())[:3]))
            context_parts.append(f"{header}\n{doc.get('content','')}")
        context_str = "\n\n".join(context_parts)

        # metrics summary
        metrics_str = ""
        if metrics:
            metrics_str = "\n\nMetrics:\n" + "\n".join(f"- {k}: {v}" for k, v in metrics.items() if v is not None)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial analyst assistant specializing in private equity fund performance.

                Your role:
                - Answer questions about fund performance using provided context
                - Calculate metrics like DPI, IRR when asked
                - Explain complex financial terms in simple language
                - Always cite your sources from the provided documents

                When calculating:
                - Use the provided metrics data
                - Show your work step-by-step
                - Explain any assumptions made

                Format your responses:
                - Be concise but thorough
                - Use bullet points for lists
                - Bold important numbers using **number**
                - Provide context for metrics"""),
                ("user", """Context from documents:
                {context}
                {metrics}
                {history}

                Question: {query}

                Please provide a helpful answer based on the context and metrics provided.""")
        ])
        
        # Generate response
        messages = prompt.format_messages(
            context=context_str,
            metrics=metrics_str,
            history=history_str,
            query=query
        )
    
        return messages
    
    async def generate(self, prompt: str, timeout: Optional[float] = None) -> str:
        """
        Generate answer from LLM.
        """
        try:
            resp = self.llm.invoke(prompt, timeout=timeout)
            if hasattr(resp, "content"):
                return resp.content
            return str(resp)
        except Exception as e:
            return f"I apologize, but I encountered an error generating a response: {str(e)}"