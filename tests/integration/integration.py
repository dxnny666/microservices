import pytest
import psycopg2
from time import sleep
from ticket_service.app import main as ticket_service
from statistics_service.app import main as statistics_service


def check_connect():
    try:
        conn = psycopg2.connect(
            dbname='TicketAirport',
            user='postgres',
            password='password',
            host='localhost',
            port='5432'
        )
        conn.close()
        return True
    except:
        return False

def test_db_connection():
    sleep(5)  # Пауза перед проверкой соединения, если это необходимо
    assert check_connect() == True, "Database connection failed"

def test_ticket_service_connection():
    r = ticket_service.ticket_alive()
    assert r.status_code == 200, "Ticket service connection failed"

def test_statistics_service_connection():
    r = statistics_service.statistics_alive()
    assert r.status_code == 200, "Statistics service connection failed"