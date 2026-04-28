"""Tests for AIService with UM Gemma4 API"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_service import AIService


class TestAIService:
    """AIService tests for Gemma4 summarization"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AIService with test API key"""
        return AIService(api_key="sk-8d8bd2869b3d4c19b734a6f5c82482aa")
    
    def test_ai_service_initialization_with_key(self):
        """Test AIService initializes with API key"""
        service = AIService(api_key="test-key-123")
        assert service.api_key == "test-key-123"
        assert service.MODEL == "gemma4-26b-16g"
        assert service.API_BASE_URL == "https://ai.cloud.um.edu.ar/api/v1"
    
    def test_ai_service_initialization_missing_key(self):
        """Test AIService initializes without key (error on API call)"""
        service = AIService(api_key=None)  # Won't error until API call
        assert service.api_key is None
    
    def test_generate_summary_no_key_raises_error(self):
        """Test that generate_summary raises error when no API key"""
        service = AIService(api_key=None)
        with pytest.raises(ValueError, match="GEMMA4_API_KEY"):
            service.generate_summary("Test text")
    
    def test_generate_summary_empty_text_raises_error(self, ai_service):
        """Test that empty text raises ValueError"""
        with pytest.raises(ValueError, match="cannot be empty"):
            ai_service.generate_summary("")
    
    def test_generate_summary_with_mocked_api(self, ai_service):
        """Test generate_summary with mocked API response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Este es un resumen de prueba."
                }
            }]
        }
        
        with patch('requests.post', return_value=mock_response):
            result = ai_service.generate_summary("Texto de prueba para resumir")
            assert result == "Este es un resumen de prueba."
    
    def test_generate_summary_api_error(self, ai_service):
        """Test generate_summary handles API errors"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with patch('requests.post', return_value=mock_response):
            with pytest.raises(ValueError, match="API error"):
                ai_service.generate_summary("Test text")
    
    def test_generate_summary_network_error(self, ai_service):
        """Test generate_summary handles network errors"""
        with patch('requests.post', side_effect=Exception("Connection failed")):
            with pytest.raises(ValueError, match="Error generating summary"):
                ai_service.generate_summary("Test text")
    
    def test_test_connection_success(self, ai_service):
        """Test connection check with successful API response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with patch('requests.post', return_value=mock_response):
            result = ai_service.test_connection()
            assert result is True
    
    def test_test_connection_failure(self, ai_service):
        """Test connection check with API failure"""
        with patch('requests.post', side_effect=Exception("Connection error")):
            with pytest.raises(ValueError, match="API connection failed"):
                ai_service.test_connection()


# Integration test - only runs if API key is available
class TestAIServiceIntegration:
    """Integration tests against real UM Gemma4 API"""
    
    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_real_api_connection(self):
        """Test real connection to UM Gemma4 API"""
        import os
        api_key = os.getenv("GEMMA4_API_KEY")
        
        if not api_key:
            pytest.skip("GEMMA4_API_KEY not set")
        
        service = AIService(api_key=api_key)
        
        # Test connection
        assert service.test_connection() is True
    
    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_real_summarization(self):
        """Test real summarization with UM Gemma4 API"""
        import os
        api_key = os.getenv("GEMMA4_API_KEY")
        
        if not api_key:
            pytest.skip("GEMMA4_API_KEY not set")
        
        service = AIService(api_key=api_key)
        
        test_text = "Python es un lenguaje de programación de alto nivel conocido por su sintaxis simple y legible. Se utiliza ampliamente en ciencia de datos, desarrollo web, automatización y más."
        
        summary = service.generate_summary(test_text, max_tokens=50)
        
        assert summary is not None
        assert len(summary) > 0
        assert len(summary) < 500  # Should be a summary, not too long
