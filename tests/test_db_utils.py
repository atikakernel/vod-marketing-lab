import os
import pytest
import pandas as pd
import pyodbc
from utils.db import get_sqlserver_conn, load_table

# --- CREDENCIALES DESDE ENTORNO ----------------------
server   = os.getenv("SERVER",   "vod-marketing-server.database.windows.net")
database = os.getenv("DATABASE", "vod_marketing_db")
user     = os.getenv("USER",  "dbadmin")
pwd      = os.getenv("PWD",   "@Infernity1")

# ----- ¡LÍNEA DE DEPURACIÓN AÑADIDA! -----
print(f"DEBUG INFO: SERVER='{server}', DATABASE='{database}', USER='{user}', PWD_FROM_ENV='{pwd}'")
# -----------------------------------------

@pytest.fixture(scope="module")
def conn():
    db_conn = None
    try:
        # Para depuración adicional, imprimimos justo antes de conectar
        print(f"DEBUG FIXTURE: Attempting connection with: server='{server}', database='{database}', user='{user}', pwd='{pwd}'")
        db_conn = get_sqlserver_conn(server, database, user, pwd)
        cur = db_conn.cursor()
        cur.execute("""
        IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Sales')
            EXEC('CREATE SCHEMA Sales');
        """)
        db_conn.commit()
        cur.execute("""
        IF OBJECT_ID('Sales.Orders', 'U') IS NULL
            CREATE TABLE Sales.Orders (
                OrderID INT IDENTITY PRIMARY KEY,
                CustomerName NVARCHAR(100),
                Amount DECIMAL(10,2),
                OrderDate DATETIME2
            );
        """)
        db_conn.commit()
        cur.execute("DELETE FROM Sales.Orders;")
        cur.execute("""
        INSERT INTO Sales.Orders (CustomerName, Amount, OrderDate)
        VALUES ('Test1',100.00,GETDATE()),('Test2',50.50,GETDATE());
        """)
        db_conn.commit()
        cur.close()
        yield db_conn
    except pyodbc.Error as e:
        print(f"Error de conexión a la base de datos durante el setup del fixture: {e}")
        # La siguiente línea ya la tenías y es útil:
        print(f"Intentando conectar a SERVER='{server}', DATABASE='{database}', USER='{user}'")
        pytest.fail(f"No se pudo conectar o configurar la base de datos para las pruebas: {e}")
    finally:
        if db_conn:
            db_conn.close()

def test_get_sqlserver_conn(conn):
    assert conn is not None, "La conexión no debería ser None"
    cur = None
    try:
        cur = conn.cursor()
        assert hasattr(cur, 'execute'), "El cursor debería tener el método 'execute'"
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result[0] == 1, "La consulta de prueba 'SELECT 1' falló"
    except pyodbc.Error as e:
        pytest.fail(f"Error al interactuar con la base de datos en test_get_sqlserver_conn: {e}")
    finally:
        if cur:
            cur.close()

def test_load_table_returns_dataframe(conn):
    try:
        df = load_table(conn, 'Sales.Orders', top_n=2)
        assert isinstance(df, pd.DataFrame), "load_table debería devolver un DataFrame"
        assert len(df) == 2, "Debería cargar 2 filas según top_n=2 y los datos insertados"
        expected_columns = ['OrderID', 'CustomerName', 'Amount', 'OrderDate']
        for col in expected_columns:
            assert col in df.columns, f"La columna '{col}' falta en el DataFrame"
    except pyodbc.Error as e:
        pytest.fail(f"Error de base de datos durante test_load_table_returns_dataframe: {e}")
    except Exception as e:
        pytest.fail(f"Error inesperado en test_load_table_returns_dataframe: {e}")

