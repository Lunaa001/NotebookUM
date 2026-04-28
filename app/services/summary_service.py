"""
Summary Service - Handles document summarization via AI
"""
import logging
from app.services.ai_service import AIService


logger = logging.getLogger(__name__)


class SummaryService:
    """Service for generating summaries of documents using AI"""
    
    def __init__(self, ai_service: AIService = None):
        """
        Initialize SummaryService
        
        Args:
            ai_service: AIService instance (optional for dependency injection)
        """
        self.ai_service = ai_service
    
    def generate_summary(self, document_text: str, max_tokens: int = 300) -> str:
        """
        Generate a concise summary of document text using Gemma4 API
        
        Args:
            document_text: Full text extracted from document
            max_tokens: Maximum tokens for summary (default 300)
            
        Returns:
            Generated summary text
            
        Raises:
            ValueError: If text is empty or too short
            RuntimeError: If AI service is not initialized
        """
        if not document_text or not document_text.strip():
            raise ValueError("Document text cannot be empty")
        
        if not self.ai_service:
            raise RuntimeError("AIService not initialized. Cannot generate summary.")
        
        logger.info(f"Generating summary for {len(document_text)} characters")
        
        try:
            summary = self.ai_service.generate_summary(
                text=document_text,
                max_tokens=max_tokens
            )
            logger.info(f"Summary generated: {len(summary)} characters")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
    
    def should_generate_summary(self, document_text: str, min_length: int = 100) -> bool:
        """
        Determine if a document should be summarized (quality check)
        
        Args:
            document_text: Document text to check
            min_length: Minimum length required (default 100 chars)
            
        Returns:
            True if document meets criteria for summarization
        """
        if not document_text:
            return False
        
        clean_text = document_text.strip()
        return len(clean_text) >= min_length
