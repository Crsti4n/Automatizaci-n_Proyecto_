import pytest
import psycopg2
from psycopg2.extras import RealDictCursor

# Datos de conexión a PostgreSQL (ajustar si cambian en docker-compose)
DB_CONFIG = {
    "dbname": "mydb",
    "user": "user",
    "password": "password",
    "host": "db",
    "port": "5432"
}

@pytest.fixture
def db_connection():
    """Configura y cierra la conexión con PostgreSQL."""
    conn = psycopg2.connect(**DB_CONFIG)
    yield conn
    conn.close()

def test_insert_and_fetch_data(db_connection):
    """Prueba insertar y recuperar datos en la tabla ropa."""
    cursor = db_connection.cursor(cursor_factory=RealDictCursor)
    
    # Insertar un nuevo registro
    cursor.execute("INSERT INTO ropa (tipo, color, talla, precio) VALUES (%s, %s, %s, %s) RETURNING id", 
                   ("Zapatos", "Azul", "M", 29.99))
    new_id = cursor.fetchone()["id"]
    db_connection.commit()

    # Verificar que el registro se insertó correctamente
    cursor.execute("SELECT * FROM ropa WHERE id = %s", (new_id,))
    result = cursor.fetchone()

    assert result is not None
    assert result["tipo"] == "Zapatos"
    assert result["color"] == "Azul"
    assert result["talla"] == "M"
    assert float(result["precio"]) == 29.99

    # Eliminar el registro después de la prueba
    cursor.execute("DELETE FROM ropa WHERE id = %s", (new_id,))
    db_connection.commit()
    cursor.close()
