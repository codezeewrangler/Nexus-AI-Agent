# app/services/vector_service.py

from typing import List, Dict, Optional
import logging

logger = logging.getLogger("nexus")


class VectorService:
    def __init__(self):
        from app.core.config import get_settings
        import chromadb
        from chromadb.config import Settings
        
        self.settings = get_settings()
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.Client(Settings(
            persist_directory=self.settings.chroma_persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="nexus_documents",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
    
    def add_document(
        self, 
        document_id: str,
        chunks: List[Dict]
    ) -> None:
        """
        Add document chunks to vector store
        
        Args:
            document_id: Unique document identifier
            chunks: List of dicts with 'chunk_id', 'content', 'embedding', 'metadata'
        """
        from app.core.exceptions import VectorStoreError
        
        try:
            ids = [f"{document_id}_{chunk['chunk_id']}" for chunk in chunks]
            embeddings = [chunk['embedding'] for chunk in chunks]
            documents = [chunk['content'] for chunk in chunks]
            metadatas = [
                {
                    **chunk.get('metadata', {}),
                    'document_id': document_id,
                    'chunk_id': chunk['chunk_id']
                }
                for chunk in chunks
            ]
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(chunks)} chunks for document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to add document to vector store: {str(e)}")
            raise VectorStoreError(f"Failed to add document: {str(e)}")
    
    def search(
        self, 
        query_embedding: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Embedding vector of query
            top_k: Number of results to return
            document_id: Optional filter by document
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of dicts with 'content', 'similarity', 'metadata'
        """
        from app.core.exceptions import VectorStoreError
        
        try:
            where_filter = None
            if document_id:
                where_filter = {"document_id": document_id}
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    # Convert distance to similarity (cosine distance to similarity)
                    distance = results['distances'][0][i] if results['distances'] else 0
                    similarity = 1 - distance
                    
                    if similarity >= min_similarity:
                        formatted_results.append({
                            'content': results['documents'][0][i],
                            'similarity': similarity,
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                            'chunk_id': results['ids'][0][i]
                        })
            
            logger.info(f"Found {len(formatted_results)} similar chunks")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise VectorStoreError(f"Search failed: {str(e)}")
    
    def delete_document(self, document_id: str) -> None:
        """Delete all chunks for a document"""
        from app.core.exceptions import VectorStoreError
        
        try:
            self.collection.delete(
                where={"document_id": document_id}
            )
            logger.info(f"Deleted document {document_id}")
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise VectorStoreError(f"Delete failed: {str(e)}")
    
    def get_document_count(self) -> int:
        """Get total number of chunks in store"""
        return self.collection.count()
