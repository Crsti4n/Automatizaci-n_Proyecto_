import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# Datos de conexión a PostgreSQL (GitHub Actions usa localhost)
DB_CONFIG = {
    "dbname": "testdb",  # Se usa 'testdb' porque en GitHub Actions se crea como testdb
    "user": "user",
    "password": "password",
    "host": "localhost",  # ⚠️ Cambiado de 'db' a 'localhost'
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
        except psycopg2.OperationalError:
            retries -= 1
            time.sleep(3)
    assert retries > 0, "❌ No se pudo conectar a PostgreSQL después de varios intentos"

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
