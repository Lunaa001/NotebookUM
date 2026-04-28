"""
Tests for SummaryService - Updated for FASE 5 AI Integration
"""
import unittest
from unittest.mock import patch, MagicMock

from app.services.summary_service import SummaryService
from app.services.ai_service import AIService


class TestSummaryServiceFASE5(unittest.TestCase):
    """Tests for the new AI-based SummaryService (FASE 5)"""
    
    def test_summary_service_initialization(self):
        """Test SummaryService can be initialized without AI service"""
        service = SummaryService()
        self.assertIsNone(service.ai_service)
    
    def test_summary_service_initialization_with_ai_service(self):
        """Test SummaryService can be initialized with AI service"""
        ai_service = AIService(api_key="test-key")
        service = SummaryService(ai_service=ai_service)
        self.assertIsNotNone(service.ai_service)
    
    def test_generate_summary_requires_ai_service(self):
        """Test generate_summary raises error without AI service"""
        service = SummaryService()  # No AI service
        
        with self.assertRaises(RuntimeError) as context:
            service.generate_summary("Test text")
        
        self.assertIn("AIService not initialized", str(context.exception))
    
    def test_generate_summary_rejects_empty_text(self):
        """Test generate_summary rejects empty text"""
        ai_service = AIService(api_key="test-key")
        service = SummaryService(ai_service=ai_service)
        
        with self.assertRaises(ValueError) as context:
            service.generate_summary("")
        
        self.assertIn("cannot be empty", str(context.exception))
    
    def test_should_generate_summary_returns_false_for_short_text(self):
        """Test should_generate_summary returns False for short text"""
        service = SummaryService()
        result = service.should_generate_summary("short", min_length=100)
        self.assertFalse(result)
    
    def test_should_generate_summary_returns_true_for_long_text(self):
        """Test should_generate_summary returns True for long text"""
        service = SummaryService()
        long_text = "a" * 200  # 200 characters
        result = service.should_generate_summary(long_text, min_length=100)
        self.assertTrue(result)
    
    def test_should_generate_summary_returns_false_for_none(self):
        """Test should_generate_summary returns False for None"""
        service = SummaryService()
        result = service.should_generate_summary(None)
        self.assertFalse(result)
    
    @patch('app.services.ai_service.requests.post')
    def test_generate_summary_with_mocked_api(self, mock_post):
        """Test generate_summary calls AI service correctly"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Generated summary text",
                        "reasoning": ""
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        ai_service = AIService(api_key="test-key")
        service = SummaryService(ai_service=ai_service)
        
        test_text = "Python is a great language. " * 10
        summary = service.generate_summary(test_text, max_tokens=100)
        
        self.assertIsNotNone(summary)
        self.assertIsInstance(summary, str)


if __name__ == "__main__":
    unittest.main()

