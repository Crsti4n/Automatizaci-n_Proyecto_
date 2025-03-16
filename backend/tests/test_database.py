import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time

# Detectar si estamos en GitHub Actions
IS_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

# Configuración dinámica del host de PostgreSQL
DB_HOST = "localhost" if IS_GITHUB_ACTIONS else "postgres-db"  # 🔹 Usar siempre postgres-db en local

DB_CONFIG = {
    "dbname": "testdb",
    "user": "user",
    "password": "password",
    "host": DB_HOST,
    "port": "5432"
}

@pytest.fixture(scope="module")
def db_connection():
    """Configura y cierra la conexión con PostgreSQL."""
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            yield conn
            conn.close()
            break
        except psycopg2.OperationalError as e:
            print(f"❌ Error de conexión a PostgreSQL ({DB_HOST}): {e}")
            retries -= 1
            time.sleep(3)
    assert retries > 0, f"❌ No se pudo conectar a PostgreSQL en {DB_HOST} después de varios intentos"

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
