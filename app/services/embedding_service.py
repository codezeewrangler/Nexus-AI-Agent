# app/services/embedding_service.py

from typing import List, Dict
import logging
import time

logger = logging.getLogger("nexus")


class EmbeddingService:
    def __init__(self):
        from app.core.config import get_settings
        import google.generativeai as genai
        
        self.settings = get_settings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model = self.settings.embedding_model
        self.genai = genai
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text using Gemini"""
        from app.core.exceptions import EmbeddingGenerationError
        
        try:
            result = self.genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise EmbeddingGenerationError(f"Failed to generate embedding: {str(e)}")
    
    def generate_query_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text using Gemini"""
        from app.core.exceptions import EmbeddingGenerationError
        
        try:
            result = self.genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Query embedding generation failed: {str(e)}")
            raise EmbeddingGenerationError(f"Failed to generate query embedding: {str(e)}")
    
    def generate_embeddings_batch(
        self, 
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Processes in batches to avoid rate limits
        """
        from app.core.exceptions import EmbeddingGenerationError
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Gemini batch embedding
                result = self.genai.embed_content(
                    model=self.model,
                    content=batch,
                    task_type="retrieval_document"
                )
                
                # Handle both single and batch results
                if 'embeddings' in result:
                    all_embeddings.extend(result['embeddings'])
                else:
                    all_embeddings.append(result['embedding'])
                
                # Rate limiting
                if i + batch_size < len(texts):
                    time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Batch embedding failed at index {i}: {str(e)}")
                raise EmbeddingGenerationError(
                    f"Batch embedding failed: {str(e)}"
                )
        
        return all_embeddings
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add embeddings to chunks
        
        Args:
            chunks: List of dicts with 'content' key
        
        Returns:
            Same chunks with 'embedding' added
        """
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.generate_embeddings_batch(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding
        
        return chunks
