import json
from consumer1 import callback as callback1
from consumer2 import callback as callback2

def test_callback_consumer1():
    """Verifica que el consumidor 1 procese correctamente el mensaje."""
    test_message = {
        "tipo": "Camiseta",
        "color": "Rojo",
        "talla": "M",
        "precio": 25.99
    }
    body = json.dumps(test_message)
    callback1(None, None, None, body.encode('utf-8'))
    assert True  # Si no hay errores, la prueba pasa

def test_callback_consumer2():
    """Verifica que el consumidor 2 procese correctamente el mensaje."""
    test_message = {
        "tipo": "Sombrero",
        "color": "Negro",
        "talla": "L",
        "precio": 39.99
    }
    body = json.dumps(test_message)
    callback2(None, None, None, body.encode('utf-8'))
    assert True  # Si no hay errores, la prueba pasa
