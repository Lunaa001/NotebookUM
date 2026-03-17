import unittest
from app import create_app
from config import TestingConfig

class TestExample(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
    
    def test_get_all(self):
        response = self.client.get('/api/example/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
    
if __name__ == '__main__':
    unittest.main()