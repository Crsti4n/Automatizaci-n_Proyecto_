import sys
sys.path.append("/backend")  # Asegura que el backend esté en el path de Python

from fastapi.testclient import TestClient
from backend.app import app
import pytest
import app as app_module

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Limpia la base de datos antes de cada prueba."""
    session = app_module.SessionLocal()
    session.query(app_module.Ropa).delete()
    session.commit()
    session.close()

def test_obtener_productos_vacia():
    response = client.get("/productos/")
    assert response.status_code == 200
    assert response.json() == []

def test_agregar_producto():
    producto = {
        "tipo": "Camiseta",
        "color": "Azul",
        "talla": "M",
        "precio": 19.99
    }
    response = client.post("/productos/", params=producto)
    assert response.status_code == 200
    assert response.json() == {"message": "Producto agregado correctamente"}

def test_obtener_productos():
    test_agregar_producto()
    response = client.get("/productos/")
    assert response.status_code == 200
    productos = response.json()
    assert len(productos) == 1
    assert productos[0]["tipo"] == "Camiseta"
