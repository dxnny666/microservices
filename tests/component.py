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

    def add_ticket(self):
        res = requests.post(add_ticket_url, json=ticket)
        self.assertEqual(res, "Success")

    def test_ticket_get(self):
        res = requests.get(f"{get_ticket_by_id_url}?ticket_id={ticket['id']}")
        data = res.json()
        self.assertEqual(data['passenger_name'], "Boyarkov")
        self.assertEqual(data['passport'], "010101.010101")
        self.assertEqual(data['id_airplane'], 17)
        self.assertEqual(data['direction'], "New York")

    def fetch_tickets(self):
        res = requests.get(get_tickets_url)
        self.assertTrue(res != "Cant access database!")


if __name__ == '__main__':
    unittest.main()
