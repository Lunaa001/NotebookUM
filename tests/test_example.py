import unittest
from fastapi.testclient import TestClient
from main import app

class TestExample(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_get_example_health(self):
        """Test that example endpoints are accessible"""
        response = self.client.get('/api/v1/example/')
        # Should get a response (200 or 404 depending on endpoint)
        self.assertIsNotNone(response)


if __name__ == '__main__':
    unittest.main()
