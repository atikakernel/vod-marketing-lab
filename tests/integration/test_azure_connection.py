import os
import pytest
from utils.db import get_sqlserver_conn # Asumiendo que utils está en tu PYTHONPATH

# Credenciales para Azure SQL desde variables de entorno (definidas en el job 'integration')
AZURE_SERVER = os.getenv("SERVER")
AZURE_DATABASE = os.getenv("DATABASE")
AZURE_USER = os.getenv("USER")
AZURE_SQL_PASSWORD = os.getenv("SQL_PASSWORD")

@pytest.mark.integration # Opcional: marcar como test de integración
def test_azure_sql_connection():
    """Prueba la conexión básica a Azure SQL."""
    assert all([AZURE_SERVER, AZURE_DATABASE, AZURE_USER, AZURE_SQL_PASSWORD]), \
        "Las variables de entorno para Azure SQL no están todas definidas."

    conn = None
    try:
        conn = get_sqlserver_conn(
            server=AZURE_SERVER,
            database=AZURE_DATABASE,
            user=AZURE_USER,
            pwd=AZURE_SQL_PASSWORD
        )
        assert conn is not None
        # Opcional: ejecutar una consulta simple
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        assert row[0] == 1
        cursor.close()
    except Exception as e:
        pytest.fail(f"Error conectando o consultando Azure SQL: {e}")
    finally:
        if conn:
            conn.close()