# app/utils/chunking.py

from typing import List, Dict
import re


class TextChunker:
    def __init__(self):
        from app.core.config import get_settings
        self.settings = get_settings()
        self.chunk_size = self.settings.chunk_size
        self.overlap = self.settings.chunk_overlap
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks(
        self, 
        text: str, 
        metadata: Dict = None
    ) -> List[Dict]:
        """
        Create overlapping chunks from text
        
        Returns:
            List of dicts with 'content' and 'metadata'
        """
        sentences = self.split_into_sentences(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk size, save chunk
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'content': chunk_text,
                    'metadata': metadata or {}
                })
                
                # Keep last few sentences for overlap
                overlap_length = 0
                overlap_sentences = []
                for sent in reversed(current_chunk):
                    if overlap_length + len(sent) <= self.overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_length += len(sent)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_length = overlap_length
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'content': chunk_text,
                'metadata': metadata or {}
            })
        
        return chunks
    
    def chunk_document(self, document_data: Dict) -> List[Dict]:
        """
        Chunk entire document, preserving page/paragraph info
        
        Args:
            document_data: Output from DocumentService.parse_document()
        
        Returns:
            List of chunks with metadata
        """
        all_chunks = []
        
        # Handle PDF (has pages)
        if 'pages' in document_data:
            for page in document_data['pages']:
                page_chunks = self.create_chunks(
                    page['content'],
                    metadata={'page_number': page['page_number']}
                )
                all_chunks.extend(page_chunks)
        
        # Handle DOCX/TXT (no pages)
        else:
            chunks = self.create_chunks(
                document_data['content'],
                metadata={}
            )
            all_chunks.extend(chunks)
        
        # Add chunk IDs
        for idx, chunk in enumerate(all_chunks):
            chunk['chunk_id'] = f"chunk_{idx}"
        
        return all_chunks
