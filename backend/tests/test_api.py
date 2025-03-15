from fastapi.testclient import TestClient
from main import app  # Importamos la app FastAPI

client = TestClient(app)

def test_obtener_productos_vacia():
    """Verifica que al inicio la lista de productos esté vacía."""
    response = client.get("/productos/")
    assert response.status_code == 200
    assert response.json() == []

def test_agregar_producto():
    """Prueba la creación de un producto."""
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
    """Verifica que el producto agregado aparece en la lista."""
    response = client.get("/productos/")
    assert response.status_code == 200
    productos = response.json()
    assert len(productos) == 1
    assert productos[0]["tipo"] == "Camiseta"
    assert productos[0]["color"] == "Azul"
    assert productos[0]["talla"] == "M"
    assert productos[0]["precio"] == 19.99
