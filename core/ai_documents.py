#!/usr/bin/env python3
"""
AI Documents Manager
Wyszukiwanie semantyczne w dokumentach, analiza, przetwarzanie
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class AIDocumentsManager:
    """Manager for AI document processing and semantic search"""
    
    def __init__(self):
        self.embedding_model = None
        self.document_embeddings = {}
        self.document_index = {}
        
    async def initialize(self):
        """Initialize the AI documents manager"""
        try:
            logger.info("Initializing AI Documents Manager...")
            
            # Initialize sentence transformer model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("AI Documents Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Documents Manager: {e}")
            raise
    
    async def search_documents(self, query: str, documents: List[str], 
                             max_results: int = 10, similarity_threshold: float = 0.7,
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform semantic search in documents"""
        try:
            # Process documents
            processed_docs = await self._process_documents(documents)
            
            # Generate embeddings
            query_embedding = await self._generate_embedding(query)
            doc_embeddings = await self._generate_document_embeddings(processed_docs)
            
            # Calculate similarities
            similarities = await self._calculate_similarities(query_embedding, doc_embeddings)
            
            # Filter and rank results
            results = await self._filter_and_rank_results(
                processed_docs, similarities, similarity_threshold, max_results
            )
            
            # Store search data
            await self._store_search_data(user_id, query, results)
            
            return {
                "results": results,
                "total_found": len(results),
                "query": query,
                "similarity_threshold": similarity_threshold
            }
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            raise
    
    async def _process_documents(self, documents: List[str]) -> List[Dict[str, Any]]:
        """Process documents for search"""
        try:
            processed = []
            
            for i, doc in enumerate(documents):
                # In a real implementation, you would:
                # 1. Parse different document formats (PDF, DOCX, TXT, etc.)
                # 2. Extract text content
                # 3. Clean and preprocess text
                # 4. Split into chunks if needed
                
                processed_doc = {
                    "id": f"doc_{i}",
                    "content": doc,  # Simplified - would be extracted text
                    "title": f"Document {i+1}",
                    "type": "text",
                    "chunks": [doc],  # Would be split into chunks
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "word_count": len(doc.split()),
                        "language": "pl"
                    }
                }
                
                processed.append(processed_doc)
            
            return processed
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return []
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        try:
            if self.embedding_model is None:
                raise ValueError("Embedding model not initialized")
            
            # Generate embedding
            embedding = self.embedding_model.encode(text)
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return np.array([])
    
    async def _generate_document_embeddings(self, documents: List[Dict[str, Any]]) -> List[np.ndarray]:
        """Generate embeddings for documents"""
        try:
            embeddings = []
            
            for doc in documents:
                # Generate embedding for each chunk
                doc_embeddings = []
                for chunk in doc["chunks"]:
                    embedding = await self._generate_embedding(chunk)
                    doc_embeddings.append(embedding)
                
                # Average embeddings for the document
                if doc_embeddings:
                    avg_embedding = np.mean(doc_embeddings, axis=0)
                    embeddings.append(avg_embedding)
                else:
                    embeddings.append(np.array([]))
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Document embeddings generation failed: {e}")
            return []
    
    async def _calculate_similarities(self, query_embedding: np.ndarray, 
                                    doc_embeddings: List[np.ndarray]) -> List[float]:
        """Calculate similarities between query and documents"""
        try:
            similarities = []
            
            for doc_embedding in doc_embeddings:
                if len(doc_embedding) > 0 and len(query_embedding) > 0:
                    # Calculate cosine similarity
                    similarity = np.dot(query_embedding, doc_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                    )
                    similarities.append(float(similarity))
                else:
                    similarities.append(0.0)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return []
    
    async def _filter_and_rank_results(self, documents: List[Dict[str, Any]], 
                                     similarities: List[float], 
                                     threshold: float, max_results: int) -> List[Dict[str, Any]]:
        """Filter and rank search results"""
        try:
            # Combine documents with similarities
            doc_similarities = list(zip(documents, similarities))
            
            # Filter by threshold
            filtered = [(doc, sim) for doc, sim in doc_similarities if sim >= threshold]
            
            # Sort by similarity (descending)
            filtered.sort(key=lambda x: x[1], reverse=True)
            
            # Limit results
            limited = filtered[:max_results]
            
            # Format results
            results = []
            for doc, similarity in limited:
                result = {
                    "document_id": doc["id"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "similarity_score": similarity,
                    "metadata": doc["metadata"],
                    "excerpt": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Result filtering and ranking failed: {e}")
            return []
    
    async def _store_search_data(self, user_id: Optional[str], query: str, results: List[Dict[str, Any]]):
        """Store search data for analytics"""
        try:
            search_data = {
                "user_id": user_id,
                "query": query,
                "results_count": len(results),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Search data stored for user {user_id}")
            
        except Exception as e:
            logger.error(f"Search data storage failed: {e}")
    
    async def cleanup(self):
        """Cleanup AI documents manager"""
        try:
            logger.info("AI Documents Manager cleaned up successfully")
        except Exception as e:
            logger.error(f"AI Documents Manager cleanup failed: {e}")