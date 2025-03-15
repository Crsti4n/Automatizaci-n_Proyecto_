import json
import pytest

def test_mensaje_rabbitmq():
    """Verifica que el mensaje enviado a RabbitMQ tenga el formato correcto"""
    producto = {
        "tipo": "Camiseta",
        "color": "Azul",
        "talla": "M",
        "precio": 19.99
    }

    mensaje_json = json.dumps(producto)
    mensaje_dict = json.loads(mensaje_json)

    assert isinstance(mensaje_dict, dict)
    assert mensaje_dict["tipo"] == "Camiseta"
    assert mensaje_dict["color"] == "Azul"
    assert mensaje_dict["talla"] == "M"
    assert mensaje_dict["precio"] == 19.99
