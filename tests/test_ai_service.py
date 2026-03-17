import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from config import TestingConfig


class TestAIService(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

    @patch("app.services.ai_service.requests.post")
    def test_ai_query_returns_response_from_gemma3_4b(self, mock_post):
        """El endpoint debe conectar con gemma3-4b y obtener una respuesta"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Hola! Estoy bien, gracias por preguntar."}}
            ]
        }
        mock_post.return_value = mock_response

        response = self.client.post(
            "/api/ai/query", json={"prompt": "Hola, ¿cómo estás?"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json)
        self.assertIsNotNone(response.json["response"])
        self.assertIsInstance(response.json["response"], str)
        self.assertEqual(
            response.json["response"], "Hola! Estoy bien, gracias por preguntar."
        )


if __name__ == "__main__":
    unittest.main()
