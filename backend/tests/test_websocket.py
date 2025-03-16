from app import send_to_clients  # Asegura que no se ejecuta `Base.metadata.create_all()`
from unittest.mock import AsyncMock
import pytest

@pytest.mark.asyncio
async def test_websocket_error():
    """Prueba que send_to_clients maneja errores en WebSocket"""
    mock_client = AsyncMock()
    mock_client.send_text.side_effect = Exception("Error en WebSocket")
    
    clients = [mock_client]
    await send_to_clients("Test message", clients, "Consumer 1")

    assert mock_client.send_text.call_count == 1
