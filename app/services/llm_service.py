# app/services/llm_service.py

from typing import List, Dict
import logging

logger = logging.getLogger("nexus")


class LLMService:
    def __init__(self):
        from app.core.config import get_settings
        import google.generativeai as genai
        
        self.settings = get_settings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model_name = self.settings.llm_model
        self.genai = genai
    
    def create_prompt(
        self, 
        query: str, 
        context_chunks: List[Dict]
    ) -> str:
        """
        Create prompt with retrieved context
        
        Args:
            query: User's question
            context_chunks: Relevant chunks from vector search
        
        Returns:
            Formatted prompt
        """
        # Build context section with citations
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            page = chunk['metadata'].get('page_number', 'N/A')
            similarity = chunk['similarity']
            content = chunk['content']
            
            context_parts.append(
                f"[Source {i}, Page {page}, Relevance: {similarity:.2f}]\n{content}"
            )
        
        context_text = "\n\n".join(context_parts)
        
        prompt = f"""CONTEXT FROM DOCUMENTS:
{context_text}

USER QUESTION:
{query}

INSTRUCTIONS:
1. Answer the question using ONLY information from the context above
2. If the context doesn't contain relevant information, say "I don't have enough information to answer this question"
3. Cite sources by referencing [Source X] numbers
4. Be concise and accurate
5. Include page numbers when mentioning specific information

ANSWER:"""
        
        return prompt
    
    def generate_answer(
        self, 
        query: str, 
        context_chunks: List[Dict]
    ) -> Dict:
        """
        Generate answer using LLM
        
        Returns:
            Dict with 'answer' and 'metadata' (token usage, model, etc)
        """
        from app.core.exceptions import LLMError
        
        try:
            prompt = self.create_prompt(query, context_chunks)
            
            # Create Gemini model with system instruction
            model = self.genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction="You are a helpful document assistant that provides accurate answers based on the provided context."
            )
            
            generation_config = self.genai.GenerationConfig(
                temperature=self.settings.llm_temperature,
                max_output_tokens=self.settings.max_tokens
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            answer = response.text
            
            # Estimate tokens (Gemini doesn't provide exact count in same way as OpenAI)
            # Using rough estimation: ~4 characters per token
            prompt_tokens = len(prompt) // 4
            completion_tokens = len(answer) // 4
            
            return {
                'answer': answer,
                'metadata': {
                    'model': self.model_name,
                    'tokens_used': prompt_tokens + completion_tokens,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise LLMError(f"Failed to generate answer: {str(e)}")
