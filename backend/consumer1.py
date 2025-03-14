import pika  # Cliente de RabbitMQ
import json  # Para manejar datos en formato JSON
import asyncio  # Para manejar tareas asíncronas
import websockets  # Para enviar mensajes a la interfaz en tiempo real

async def enviar_websocket(mensaje):
    """Función asíncrona para enviar mensajes a WebSocket de Consumer 1"""
    uri = "ws://python-rabbitmq-container:8000/ws/consumer1"

    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(mensaje)  # Enviar mensaje JSON al WebSocket
            print(f"✅ Mensaje enviado al WebSocket: {mensaje}")
    except Exception as e:
        print(f"❌ Error enviando mensaje al WebSocket: {e}")

def callback(ch, method, properties, body):
    """Callback que se ejecuta al recibir un mensaje de RabbitMQ"""
    ropa = json.loads(body)  # Convertir mensaje de JSON a diccionario
    print(f"[x] Consumidor 1 recibió: {ropa}")
    asyncio.run(enviar_websocket(json.dumps(ropa)))  # Enviar mensaje a WebSocket

# Conectar a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-container'))
channel = connection.channel()

# Asegurar que la cola "ropa" existe
channel.queue_declare(queue='ropa')

# Suscribirse a la cola y definir la función callback para procesar los mensajes
channel.basic_consume(queue='ropa', on_message_callback=callback, auto_ack=True)

print("[*] Esperando mensajes en Consumer 1. Para salir presiona CTRL+C")
channel.start_consuming()  # Inicia el consumo de mensajes (bloquea ejecución)

