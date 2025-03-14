import pika
import json
import random
import time

# Lista de tipos de ropa y colores
tipos_ropa = ["Camiseta", "Pantalón", "Zapatos", "Chaqueta", "Sombrero"]
colores = ["Rojo", "Azul", "Verde", "Negro", "Blanco"]
tallas = ["S", "M", "L", "XL"]

# Conectar a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-container'))
channel = connection.channel()

# Declarar la cola
channel.queue_declare(queue='ropa')

def generar_ropa():
    """Genera un objeto de ropa con datos aleatorios"""
    return {
        "tipo": random.choice(tipos_ropa),
        "color": random.choice(colores),
        "talla": random.choice(tallas),
        "precio": round(random.uniform(10, 100), 2)  # Precio entre 10 y 100
    }

# Enviar objetos aleatorios a la cola
for i in range(10):
    ropa = generar_ropa()
    message = json.dumps(ropa)  # Convertir a JSON
    channel.basic_publish(exchange='', routing_key='ropa', body=message)
    print(f"[x] Enviado: {message}")
    time.sleep(2)  # Pausa de 2 segundos entre envíos

# Cerrar conexión
connection.close()

