from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
import asyncio
import json
import pika
import threading
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

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

# Inicializar la base de datos (solo si es necesario)
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de BD
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

# Modelo de datos para la API
class Producto(BaseModel):
    tipo: str
    color: str
    talla: str
    precio: float

# Listas de clientes WebSocket conectados
clients_consumer1 = set()
clients_consumer2 = set()

async def websocket_handler(websocket: WebSocket, clients: set, consumer_name: str):
    """Maneja conexiones WebSocket y mantiene a los clientes en la lista."""
    await websocket.accept()
    clients.add(websocket)
    print(f"🔵 Cliente conectado a {consumer_name}. Total clientes: {len(clients)}")

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        clients.remove(websocket)
        print(f"🔴 Cliente desconectado de {consumer_name}. Total clientes: {len(clients)}")

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

    disconnected_clients = set()

    for client in clients:
        try:
            await client.send_text(message)
            print(f"✅ Mensaje enviado correctamente a {consumer_name}")
        except Exception as e:
            print(f"❌ Error enviando mensaje a {consumer_name}: {e}")
            disconnected_clients.add(client)

    clients.difference_update(disconnected_clients)

def consumer_callback(ch, method, properties, body):
    """Procesa mensajes de RabbitMQ y los reenvía a los WebSockets"""
    try:
        producto = json.loads(body)
        print(f"[x] Recibido: {producto}")

        tipo_producto = producto.get("tipo", "").lower()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if tipo_producto in ["camiseta", "pantalón", "chaqueta"]:
            loop.run_until_complete(send_to_clients(json.dumps(producto), clients_consumer1, "Consumer 1"))
        elif tipo_producto in ["sombrero", "zapatos"]:
            loop.run_until_complete(send_to_clients(json.dumps(producto), clients_consumer2, "Consumer 2"))

        # Guardar mensaje en la base de datos
        db = SessionLocal()
        nuevo_producto = Ropa(**producto)
        db.add(nuevo_producto)
        db.commit()
        db.close()

    except Exception as e:
        print(f"❌ Error procesando mensaje de RabbitMQ: {e}")

def start_consumer():
    """Se conecta a RabbitMQ y escucha la cola 'ropa' en un hilo separado"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq-container"))
    channel = connection.channel()
    channel.queue_declare(queue="ropa", durable=True)
    channel.basic_consume(queue="ropa", on_message_callback=consumer_callback, auto_ack=True)
    channel.start_consuming()

# Ejecutar el consumidor en un hilo separado
threading.Thread(target=start_consumer, daemon=True).start()

# ================================
# Endpoints para interactuar con PostgreSQL
# ================================
@app.get("/productos/")
def obtener_productos(db: Session = Depends(get_db)):
    """Obtiene todos los productos almacenados en la BD"""
    return db.query(Ropa).all()

@app.post("/productos/")
def agregar_producto(producto: Producto, db: Session = Depends(get_db)):
    """Agrega un nuevo producto a la BD"""
    nuevo_producto = Ropa(**producto.dict())
    db.add(nuevo_producto)
    db.commit()
    return {"message": "Producto agregado correctamente"}

# ================================
# Iniciar la aplicación
# ================================
if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
