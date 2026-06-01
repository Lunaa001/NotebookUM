"""Tests for AIService with UM OpenAI-compatible API"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_service import AIService


class TestAIService:
    """AIService tests for OpenAI-compatible API summarization"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AIService with test API key"""
        return AIService(api_key="sk-8d8bd2869b3d4c19b734a6f5c82482aa")
    
    def test_ai_service_initialization_with_key(self):
        """Test AIService initializes with API key"""
        service = AIService(api_key="test-key-123")
        assert service.api_key == "test-key-123"
        assert service.MODEL == "gemma4-26b"
        assert service.API_BASE_URL == "https://ai.cloud.um.edu.ar/api/v1"
    
    def test_ai_service_initialization_missing_key(self):
        """Test AIService initializes without key (error on API call)"""
        # Mock os.getenv in ai_service module to ensure OPENAI_API_KEY is not found
        with patch('app.services.ai_service.os.getenv', return_value=None):
            service = AIService(api_key=None)  # Won't error until API call
            assert service.api_key is None
    
    def test_generate_summary_no_key_raises_error(self):
        """Test that generate_summary raises error when no API key"""
        # Mock os.getenv in ai_service module to ensure OPENAI_API_KEY is not found
        with patch('app.services.ai_service.os.getenv', return_value=None):
            service = AIService(api_key=None)
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
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
        
        # Mock both health check (GET) and API call (POST)
        with patch('app.services.ai_service.AIService._check_api_health', return_value=True):
            with patch('requests.post', return_value=mock_response):
                result = ai_service.generate_summary("Texto de prueba para resumir")
                assert result == "Este es un resumen de prueba."
    
    def test_generate_summary_api_error(self, ai_service):
        """Test generate_summary handles API errors"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        # Mock health check to pass, then POST fails
        with patch('app.services.ai_service.AIService._check_api_health', return_value=True):
            with patch('requests.post', return_value=mock_response):
                with pytest.raises(ValueError, match="API error"):
                    ai_service.generate_summary("Test text")
    
    def test_generate_summary_network_error(self, ai_service):
        """Test generate_summary handles network errors"""
        # Mock health check to pass, then POST raises exception
        with patch('app.services.ai_service.AIService._check_api_health', return_value=True):
            with patch('requests.post', side_effect=Exception("Connection failed")):
                with pytest.raises(ValueError, match="Error generating summary"):
                    ai_service.generate_summary("Test text")
    
    def test_test_connection_success(self, ai_service):
        """Test connection check with successful API response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Mock the health check GET request
        with patch('requests.get', return_value=mock_response):
            result = ai_service.test_connection()
            assert result is True
    
    def test_test_connection_failure(self, ai_service):
        """Test connection check with API failure"""
        # Mock health check to fail (API not reachable)
        with patch('requests.get', side_effect=Exception("Connection error")):
            result = ai_service.test_connection()
            # test_connection returns False on network error (from _check_api_health)
            assert result is False


# Integration test - only runs if API key is available
class TestAIServiceIntegration:
    """Integration tests against real UM OpenAI-compatible API"""
    
    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_real_api_connection(self):
        """Test real connection to OpenAI API"""
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")
        
        service = AIService(api_key=api_key)
        
        # Test connection
        assert service.test_connection() is True
    
    @pytest.mark.skip(reason="Integration test - requires live API")
    def test_real_summarization(self):
        """Test real summarization with OpenAI API"""
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")
        
        service = AIService(api_key=api_key)
        
        test_text = "Python es un lenguaje de programación de alto nivel conocido por su sintaxis simple y legible. Se utiliza ampliamente en ciencia de datos, desarrollo web, automatización y más."
        
        summary = service.generate_summary(test_text, max_tokens=50)
        
        assert summary is not None
        assert len(summary) > 0
        assert len(summary) < 500  # Should be a summary, not too long
