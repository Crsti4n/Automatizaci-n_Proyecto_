import pika
import json
import asyncio
import websockets

async def enviar_websocket(mensaje):
    uri = "ws://python-rabbitmq-container:8000/ws/consumer2"

    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(mensaje)
            print(f"✅ Mensaje enviado al WebSocket: {mensaje}")
    except Exception as e:
        print(f"❌ Error enviando mensaje al WebSocket: {e}")

def callback(ch, method, properties, body):
    ropa = json.loads(body)
    print(f"[x] Consumidor 2 recibió: {ropa}")
    asyncio.run(enviar_websocket(json.dumps(ropa)))

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-container'))
channel = connection.channel()
channel.queue_declare(queue='ropa')
channel.basic_consume(queue='ropa', on_message_callback=callback, auto_ack=True)

print("[*] Esperando mensajes en Consumer 2. Para salir presiona CTRL+C")
channel.start_consuming()

