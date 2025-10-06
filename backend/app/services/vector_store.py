"""
Vector store service using FAISS
"""
import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings


class VectorStore:
    """FAISS-based vector store for document embeddings"""
    
    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        self.metadata_path = f"{self.index_path}/metadata.pkl"
        self.index = None
        self.metadata = []
        self.embeddings = self._initialize_embeddings()
        self._load_or_create_index()
    
    def _initialize_embeddings(self):
        """Initialize embedding model"""
        if settings.OPENAI_API_KEY:
            return OpenAIEmbeddings(
                model=settings.OPENAI_EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            # Fallback to local embeddings
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        os.makedirs(self.index_path, exist_ok=True)
        
        index_file = f"{self.index_path}/index.faiss"
        
        if os.path.exists(index_file) and os.path.exists(self.metadata_path):
            # Load existing index
            self.index = faiss.read_index(index_file)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            # Create new index (dimension depends on embedding model)
            dimension = 1536 if settings.OPENAI_API_KEY else 384
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata = []
    
    async def add_document(self, content: str, metadata: Dict[str, Any]):
        """Add a document to the vector store"""
        # Generate embedding
        embedding = await self._get_embedding(content)
        
        # Add to FAISS index
        self.index.add(np.array([embedding], dtype=np.float32))
        
        # Store metadata
        self.metadata.append({
            "content": content,
            **metadata
        })
        
        # Save index
        self._save_index()
    
    async def similarity_search(
        self, 
        query: str, 
        k: int = 5, 
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar documents with scores
        """
        # Generate query embedding
        query_embedding = await self._get_embedding(query)
        
        # Search in FAISS
        distances, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32), 
            k * 2  # Get more results for filtering
        )
        
        # Collect results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                doc = self.metadata[idx].copy()
                doc['score'] = float(1 / (1 + distance))  # Convert distance to similarity score
                
                # Apply filters
                if filter_metadata:
                    if all(doc.get(key) == value for key, value in filter_metadata.items()):
                        results.append(doc)
                else:
                    results.append(doc)
                
                if len(results) >= k:
                    break
        
        return results
    
    async def _get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if hasattr(self.embeddings, 'embed_query'):
            embedding = self.embeddings.embed_query(text)
        else:
            embedding = self.embeddings.encode(text)
        
        return np.array(embedding, dtype=np.float32)
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        index_file = f"{self.index_path}/index.faiss"
        faiss.write_index(self.index, index_file)
        
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def clear(self):
        """Clear the vector store"""
        dimension = 1536 if settings.OPENAI_API_KEY else 384
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []
        self._save_index()
