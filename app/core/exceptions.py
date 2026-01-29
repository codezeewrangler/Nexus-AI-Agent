# app/core/exceptions.py


class NexusException(Exception):
    """Base exception for Nexus AI Agent"""
    pass


class DocumentParsingError(NexusException):
    """Failed to parse document"""
    pass


class EmbeddingGenerationError(NexusException):
    """Failed to generate embeddings"""
    pass


class VectorStoreError(NexusException):
    """Vector database operation failed"""
    pass


class LLMError(NexusException):
    """LLM API call failed"""
    pass


class FileValidationError(NexusException):
    """File validation failed"""
    pass
