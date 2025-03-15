import sys
sys.path.append("/backend")

import json
import pytest
from unittest.mock import patch
from backend.consumer1 import callback as callback1
from backend.consumer2 import callback as callback2

@pytest.fixture
def test_message1():
    return json.dumps({
        "tipo": "Camiseta",
        "color": "Rojo",
        "talla": "M",
        "precio": 25.99
    }).encode("utf-8")

@pytest.fixture
def test_message2():
    return json.dumps({
        "tipo": "Sombrero",
        "color": "Negro",
        "talla": "L",
        "precio": 39.99
    }).encode("utf-8")

@patch("backend.consumer1.enviar_websocket", return_value=None)
@patch("backend.consumer1.SessionLocal", return_value=None)  # Mock de la BD
def test_callback_consumer1(mock_db, mock_ws, test_message1):
    callback1(None, None, None, test_message1)
    print("✅ [DEBUG] Consumer 1 ejecutó callback correctamente")
    mock_ws.assert_called()  # Verifica que al menos fue llamado

@patch("backend.consumer2.enviar_websocket", return_value=None)
@patch("backend.consumer2.SessionLocal", return_value=None)  # Mock de la BD
def test_callback_consumer2(mock_db, mock_ws, test_message2):
    callback2(None, None, None, test_message2)
    print("✅ [DEBUG] Consumer 2 ejecutó callback correctamente")
    mock_ws.assert_called()  # Verifica que al menos fue llamado
