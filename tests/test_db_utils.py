import os
import pytest
import pandas as pd
import pyodbc # Import pyodbc para poder capturar pyodbc.Error si es necesario
from utils.db import get_sqlserver_conn, load_table

# --- CREDENCIALES DESDE ENTORNO ----------------------
# Lee las variables de entorno SERVER y DATABASE.
# Si no están definidas, usa valores por defecto (útil para pruebas locales).
server   = os.getenv("SERVER",   "vod-marketing-server.database.windows.net")
database = os.getenv("DATABASE", "vod_marketing_db")

# Lee la variable de entorno USER.
user     = os.getenv("USER",  "dbadmin")

# Lee la variable de entorno SQL_PASSWORD (nombre corregido para evitar colisión con PWD del sistema).
# Si no está definida (ej. ejecución local sin esta variable seteada),
# usa un valor por defecto.
pwd      = os.getenv("SQL_PASSWORD", "@Infernity1") # Corregido: Leer "SQL_PASSWORD"
# ------------------------------------------------------

@pytest.fixture(scope="module")
def conn():
    """
    Fixture de Pytest para establecer y limpiar una conexión a la base de datos.
    Se ejecuta una vez por módulo de pruebas.
    Crea un esquema 'Sales' y una tabla 'Sales.Orders' con datos de prueba.
    """
    db_conn = None # Inicializar db_conn a None
    try:
        # Intenta establecer la conexión con las credenciales obtenidas
        db_conn = get_sqlserver_conn(server, database, user, pwd)
        cur = db_conn.cursor()

        # Asegura que el esquema 'Sales' exista
        cur.execute("""
        IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Sales')
            EXEC('CREATE SCHEMA Sales');
        """)
        db_conn.commit() # Commit para asegurar que el esquema se cree antes de crear la tabla

        # Asegura que la tabla 'Sales.Orders' exista, la limpia e inserta datos de prueba
        cur.execute("""
        IF OBJECT_ID('Sales.Orders', 'U') IS NULL
            CREATE TABLE Sales.Orders (
                OrderID INT IDENTITY PRIMARY KEY,
                CustomerName NVARCHAR(100),
                Amount DECIMAL(10,2),
                OrderDate DATETIME2
            );
        """)
        db_conn.commit() # Commit para asegurar que la tabla se cree

        cur.execute("DELETE FROM Sales.Orders;") # Limpia la tabla antes de insertar
        cur.execute("""
        INSERT INTO Sales.Orders (CustomerName, Amount, OrderDate)
        VALUES ('Test1',100.00,GETDATE()),('Test2',50.50,GETDATE());
        """)
        db_conn.commit() # Commit de la inserción de datos
        
        cur.close() # Cierra el cursor
        yield db_conn # Proporciona la conexión a las pruebas

    except pyodbc.Error as e:
        # Si hay un error de pyodbc (ej. fallo de login, problema de red),
        # se imprime un mensaje y se falla la prueba de forma controlada.
        print(f"Error de conexión a la base de datos durante el setup del fixture: {e}")
        print(f"Intentando conectar a SERVER='{server}', DATABASE='{database}', USER='{user}'") # PWD no se imprime por seguridad
        pytest.fail(f"No se pudo conectar o configurar la base de datos para las pruebas: {e}")
    
    finally:
        # Asegura que la conexión se cierre después de que todas las pruebas del módulo la hayan usado
        if db_conn:
            db_conn.close()

def test_get_sqlserver_conn(conn):
    """
    Prueba que la conexión a SQL Server se obtiene correctamente.
    Verifica que el objeto de conexión no sea None y que tenga un cursor con el método 'execute'.
    """
    assert conn is not None, "La conexión no debería ser None"
    cur = None # Inicializar cur
    try:
        cur = conn.cursor()
        assert hasattr(cur, 'execute'), "El cursor debería tener el método 'execute'"
        # Opcional: realizar una consulta simple para verificar la conexión
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result[0] == 1, "La consulta de prueba 'SELECT 1' falló"
    except pyodbc.Error as e:
        pytest.fail(f"Error al interactuar con la base de datos en test_get_sqlserver_conn: {e}")
    finally:
        if cur:
            cur.close()


def test_load_table_returns_dataframe(conn):
    """
    Prueba que la función load_table carga datos en un DataFrame de pandas correctamente.
    Verifica el tipo de objeto devuelto, el número de filas y la presencia de columnas esperadas.
    """
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
