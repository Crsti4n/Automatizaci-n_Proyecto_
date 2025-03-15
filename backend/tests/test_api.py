import sys
sys.path.append("/backend")

from fastapi.testclient import TestClient
from backend.app import app, Base, get_db, engine
import pytest
from sqlalchemy.orm import Session

client = TestClient(app)

# 🔹 Fixture para crear la base de datos antes de las pruebas
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crea la base de datos en SQLite antes de ejecutar las pruebas."""
    Base.metadata.create_all(bind=engine)

# 🔹 Fixture para limpiar la BD entre pruebas
@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Limpia la base de datos antes de cada prueba."""
    session = Session(bind=engine)
    session.query(Base.metadata.tables["ropa"]).delete()
    session.commit()
    session.close()

def test_obtener_productos_vacia():
    response = client.get("/productos/")
    assert response.status_code == 200
    assert response.json() == []

def test_agregar_producto():
    producto = {"tipo": "Camiseta", "color": "Azul", "talla": "M", "precio": 19.99}
    response = client.post("/productos/", params=producto)
    assert response.status_code == 200
    assert response.json() == {"message": "Producto agregado correctamente"}

def test_obtener_productos():
    test_agregar_producto()  # Asegurar que hay un producto antes de probar GET
    response = client.get("/productos/")
    assert response.status_code == 200
    productos = response.json()
    assert len(productos) == 1
    assert productos[0]["tipo"] == "Camiseta"
