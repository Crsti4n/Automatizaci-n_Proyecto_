import pika
import json
import asyncio
import websockets
from sqlalchemy.orm import sessionmaker
from app import Ropa, SessionLocal  # Importamos el modelo y la sesión

# Configuración de RabbitMQ
RABBITMQ_HOST = "rabbitmq-container"
QUEUE_NAME = "ropa"

async def enviar_websocket(mensaje):
    """Envía mensajes al WebSocket del Consumer 2."""
    uri = "ws://python-backend:8000/ws/consumer2"

    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(mensaje)
            print(f"✅ [Consumer 2] Mensaje enviado al WebSocket: {mensaje}")
    except Exception as e:
        print(f"❌ [Consumer 2] Error enviando mensaje al WebSocket: {e}")

def guardar_en_bd(producto):
    """Guarda el producto en la base de datos antes de confirmarlo en RabbitMQ."""
    db = SessionLocal()
    try:
        nuevo_producto = Ropa(
            tipo=producto["tipo"],
            color=producto["color"],
            talla=producto["talla"],
            precio=producto["precio"]
        )
        db.add(nuevo_producto)
        db.commit()
        print(f"✅ [Consumer 2] Producto guardado en BD: {producto}")
    except Exception as e:
        print(f"❌ [Consumer 2] Error guardando en BD: {e}")
        db.rollback()
    finally:
        db.close()

def callback(ch, method, properties, body):
    """Procesa mensajes de RabbitMQ y los guarda en la BD antes de confirmarlos."""
    try:
        producto = json.loads(body)
        print(f"[Consumer 2] 📥 Mensaje recibido: {producto}")

        # Guardar en PostgreSQL
        guardar_en_bd(producto)

        # Enviar a WebSocket
        asyncio.run(enviar_websocket(json.dumps(producto)))

        # Confirmar recepción del mensaje
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"✅ [Consumer 2] Mensaje confirmado en RabbitMQ")

    except Exception as e:
        print(f"❌ [Consumer 2] Error procesando mensaje: {e}")

def iniciar_consumidor():
    """Inicia el Consumer 2 en la cola 'ropa'."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Filtra productos solo de ciertos tipos
    def filtro_callback(ch, method, properties, body):
        producto = json.loads(body)
        if producto["tipo"].lower() in ["sombrero", "zapatos"]:
            callback(ch, method, properties, body)
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=filtro_callback)

    print(f"🔄 [Consumer 2] Esperando mensajes...")
    channel.start_consuming()

if __name__ == "__main__":
    iniciar_consumidor()
