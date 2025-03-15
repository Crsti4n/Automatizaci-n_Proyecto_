from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
import asyncio  # Para manejo de eventos asíncronos
import json  # Para manejar los datos en formato JSON
import pika  # Cliente de RabbitMQ
import threading  # Para ejecutar el consumidor en paralelo
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ================================
# Configuración de la Base de Datos PostgreSQL
# ================================
DATABASE_URL = "postgresql://user:password@db:5432/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# Modelo de la tabla "ropa"
class Ropa(Base):
    __tablename__ = "ropa"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50))
    color = Column(String(50))
    talla = Column(String(10))
    precio = Column(Float)

# Crear las tablas en la BD
Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de BD en cada solicitud
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================================
# Configuración de la Aplicación FastAPI
# ================================
app = FastAPI()

# Listas de clientes WebSocket conectados
clients_consumer1 = []
clients_consumer2 = []

async def websocket_handler(websocket: WebSocket, clients, consumer_name):
    """Maneja conexiones WebSocket y mantiene a los clientes en la lista."""
    await websocket.accept()  # Aceptar conexión entrante
    clients.append(websocket)  # Agregar cliente a la lista
    print(f"🔵 Cliente conectado a {consumer_name}. Total clientes: {len(clients)}")

    try:
        while True:
            await asyncio.sleep(1)  # Mantiene la conexión abierta
    except WebSocketDisconnect:
        clients.remove(websocket)  # Remover cliente desconectado
        print(f"🔴 Cliente desconectado de {consumer_name}. Total clientes: {len(clients)}")

# Rutas de WebSocket para consumidores
@app.websocket("/ws/consumer1")
async def websocket_consumer1(websocket: WebSocket):
    await websocket_handler(websocket, clients_consumer1, "Consumer 1")

@app.websocket("/ws/consumer2")
async def websocket_consumer2(websocket: WebSocket):
    await websocket_handler(websocket, clients_consumer2, "Consumer 2")

async def send_to_clients(message, clients, consumer_name):
    """Envía mensajes a los clientes WebSocket conectados"""
    print(f"📩 Enviando mensaje a {len(clients)} clientes de {consumer_name}...")

    if not clients:
        print(f"⚠️ No hay clientes conectados en {consumer_name}.")
        return

    disconnected_clients = []  # Lista para almacenar clientes desconectados

    for client in clients:
        try:
            await client.send_text(message)  # Enviar mensaje al cliente
            print(f"✅ Mensaje enviado correctamente a {consumer_name}")
        except Exception as e:
            print(f"❌ Error enviando mensaje a {consumer_name}: {e}")
            disconnected_clients.append(client)

    # Remover clientes desconectados
    for client in disconnected_clients:
        clients.remove(client)

def consumer_callback(ch, method, properties, body):
    """Procesa mensajes de RabbitMQ y los reenvía a los WebSockets correspondientes"""
    producto = json.loads(body)  # Convertir mensaje de RabbitMQ a JSON
    print(f"[x] Recibido: {producto}")

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Filtrar productos según el tipo y enviarlos al consumidor correcto
    tipo_producto = producto.get("tipo", "").lower()

    if tipo_producto in ["camiseta", "pantalón", "chaqueta"]:
        asyncio.run(send_to_clients(json.dumps(producto), clients_consumer1, "Consumer 1"))

    elif tipo_producto in ["sombrero", "zapatos"]:
        asyncio.run(send_to_clients(json.dumps(producto), clients_consumer2, "Consumer 2"))

    # Guardar mensaje en la base de datos
    db = SessionLocal()
    nuevo_producto = Ropa(
        tipo=producto["tipo"],
        color=producto["color"],
        talla=producto["talla"],
        precio=producto["precio"]
    )
    db.add(nuevo_producto)
    db.commit()
    db.close()

def start_consumer():
    """Se conecta a RabbitMQ y escucha la cola 'ropa' en un hilo separado"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq-container"))
    channel = connection.channel()
    channel.queue_declare(queue="ropa", durable=True)
    channel.basic_consume(queue="ropa", on_message_callback=consumer_callback, auto_ack=True)
    channel.start_consuming()  # Inicia la escucha de mensajes en RabbitMQ

# Ejecutar el consumidor en un hilo separado para no bloquear FastAPI
threading.Thread(target=start_consumer, daemon=True).start()

# ================================
# Endpoints para interactuar con PostgreSQL
# ================================
@app.get("/productos/")
def obtener_productos(db: Session = Depends(get_db)):
    """Obtiene todos los productos almacenados en la BD"""
    productos = db.query(Ropa).all()
    return productos

@app.post("/productos/")
def agregar_producto(tipo: str, color: str, talla: str, precio: float, db: Session = Depends(get_db)):
    """Agrega un nuevo producto a la BD"""
    nuevo_producto = Ropa(tipo=tipo, color=color, talla=talla, precio=precio)
    db.add(nuevo_producto)
    db.commit()
    return {"message": "Producto agregado correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
