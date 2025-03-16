import pika
import json
import time

RABBITMQ_HOST = "localhost"  # ⚠️ Cambiado de "rabbitmq-container" a "localhost"
TEST_QUEUE_NAME = "ropa_test"

def test_rabbitmq_publish_consume():
    """Prueba publicar y consumir un mensaje en una cola exclusiva de RabbitMQ."""

    # 🔹 Intentar conectar con RabbitMQ con reintentos
    retries = 5
    connection = None
    while retries > 0:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            break
        except pika.exceptions.AMQPConnectionError:
            retries -= 1
            time.sleep(3)
    assert connection is not None, "❌ No se pudo conectar a RabbitMQ después de varios intentos"

    channel = connection.channel()

    # 🔹 Crear una cola exclusiva para la prueba
    channel.queue_declare(queue=TEST_QUEUE_NAME, durable=True)

    # 🔹 Mensaje de prueba
    test_message = {"tipo": "Chaqueta", "color": "Rojo", "talla": "L", "precio": 79.99}

    # 🔹 Publicar el mensaje en la cola de prueba
    channel.basic_publish(
        exchange="",
        routing_key=TEST_QUEUE_NAME,
        body=json.dumps(test_message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print("✅ Mensaje enviado a RabbitMQ en la cola de prueba")

    # 🔹 Esperar a que el mensaje esté disponible
    time.sleep(3)

    # 🔹 Intentar recibir el mensaje de la cola de prueba
    received_message = None
    retries = 5
    while retries > 0:
        method_frame, header_frame, body = channel.basic_get(queue=TEST_QUEUE_NAME, auto_ack=True)
        if body:
            received_message = json.loads(body)
            break  # Salimos del bucle si recibimos el mensaje
        time.sleep(1)
        retries -= 1

    assert received_message is not None, "❌ No se recibió el mensaje en RabbitMQ"

    print(f"✅ Mensaje recibido en la cola de prueba: {received_message}")

    # 🔹 Validar los datos del mensaje
    assert received_message["tipo"] == "Chaqueta"
    assert received_message["color"] == "Rojo"
    assert received_message["talla"] == "L"
    assert received_message["precio"] == 79.99

    # 🔹 Eliminar la cola de prueba después del test
    channel.queue_delete(queue=TEST_QUEUE_NAME)
    print("✅ Cola de prueba eliminada")

    # 🔹 Cerrar conexión
    connection.close()
