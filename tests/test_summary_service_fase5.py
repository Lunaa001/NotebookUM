"""
End-to-end tests for FASE 5: Document Summarization
"""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.summary_service import SummaryService
from app.services.ai_service import AIService


class TestSummaryService:
    """Test SummaryService"""
    
    def test_summary_service_initialization(self):
        """Test SummaryService can be initialized"""
        ai_service = AIService(api_key="test-key")
        service = SummaryService(ai_service=ai_service)
        assert service.ai_service is not None
    
    def test_should_generate_summary_short_text(self):
        """Test should_generate_summary returns False for short text"""
        service = SummaryService()
        assert service.should_generate_summary("short", min_length=100) is False
    
    def test_should_generate_summary_long_text(self):
        """Test should_generate_summary returns True for long text"""
        service = SummaryService()
        long_text = "a" * 200  # 200 chars, meets 100 char minimum
        assert service.should_generate_summary(long_text, min_length=100) is True
    
    def test_should_generate_summary_empty_text(self):
        """Test should_generate_summary returns False for empty text"""
        service = SummaryService()
        assert service.should_generate_summary("") is False
        assert service.should_generate_summary(None) is False
    
    def test_generate_summary_no_ai_service(self):
        """Test generate_summary raises error when AIService not initialized"""
        service = SummaryService()  # No AI service
        
        with pytest.raises(RuntimeError, match="AIService not initialized"):
            service.generate_summary("some text")
    
    def test_generate_summary_empty_text(self):
        """Test generate_summary raises error for empty text"""
        ai_service = AIService(api_key="test-key")
        service = SummaryService(ai_service=ai_service)
        
        with pytest.raises(ValueError, match="cannot be empty"):
            service.generate_summary("")
    
    @patch('app.services.ai_service.AIService._check_api_health', return_value=True)
    @patch('app.services.ai_service.requests.post')
    def test_generate_summary_with_mocked_ai(self, mock_post, mock_health):
        """Test generate_summary with mocked AI API"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a mocked summary",
                        "reasoning": ""
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        ai_service = AIService(api_key="test-key")
        service = SummaryService(ai_service=ai_service)
        
        test_text = "Python is a programming language. " * 20
        summary = service.generate_summary(test_text, max_tokens=100)
        
        assert summary is not None
        assert "mocked" in summary.lower() or "summary" in summary.lower()
    
    @patch('app.services.ai_service.requests.post')
    def test_generate_summary_ai_error(self, mock_post):
        """Test generate_summary handles AI API errors"""
        mock_post.side_effect = Exception("API Connection failed")
        
        ai_service = AIService(api_key="test-key")
        service = SummaryService(ai_service=ai_service)
        
        test_text = "Test document text " * 20
        
        with pytest.raises(Exception):
            service.generate_summary(test_text)


@pytest.mark.skip(reason="Requires running database and Gemma4 API")
class TestDocumentSummaryIntegration:
    """Integration tests for document summarization endpoint"""
    
    def test_generate_summary_for_document(self):
        """Test generating summary for uploaded document"""
        # This test requires:
        # 1. Running PostgreSQL
        # 2. Running Gemma4 API with valid credentials
        # 3. Pre-uploaded document
        pass
    
    def test_summary_stored_in_database(self):
        """Test that generated summary is stored in database"""
        # Verify document.resumen field is populated
        pass
    
    def test_summary_endpoint_http_response(self):
        """Test HTTP response format from summary endpoint"""
        # Test response contains: document_id, status, resumen, resumen_longitud
        pass
