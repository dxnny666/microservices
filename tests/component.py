import requests
import unittest

ticket_url = 'http://localhost:8000'
statistics_url = 'http://localhost:8001'
add_ticket_url = f'{ticket_url}/add_ticket'
get_ticket_by_id_url = f'{ticket_url}/get_ticket_by_id/'
get_tickets_url = f'{ticket_url}/get_tickets'

ticket = {
    "id": 88,
    "passenger_name": "Boyarkov",
    "passport": "010101.010101",
    "id_airplane": 17,
    "direction": "New York"
}


class TestIntegration(unittest.TestCase):
    # CMD: python tests/integration.py

    def test_ticket_service_connection(self):
        r = requests.get("http://localhost:8000/health", verify=False)
        self.assertEqual(r.status_code, 200)

    def test_statistics_service_connection(self):
        r = requests.get("http://localhost:8001/health", verify=False)
        self.assertEqual(r.status_code, 200)


if __name__ == '__main__':
    unittest.main()
