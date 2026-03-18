import unittest
import json
from api import create_app

class TestSlotsAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_get_available_slots(self):
        # Test with valid parameters
        response = self.client.get('/api/v1/slots?city=New York&date=2023-10-25')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)

    def test_missing_parameters(self):
        # Test with missing city
        response = self.client.get('/api/v1/slots?date=2023-10-25')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data.get('success', True))

        # Test with missing date
        response = self.client.get('/api/v1/slots?city=New York')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data.get('success', True))

    def test_invalid_date_format(self):
        # Test with invalid date format
        response = self.client.get('/api/v1/slots?city=New York&date=10-25-2023')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data.get('success', True))

if __name__ == '__main__':
    unittest.main()
