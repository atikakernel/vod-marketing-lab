import os
import pytest
import pandas as pd
from utils.db import get_sqlserver_conn, load_table

# Fixture para la conexión y preparación de datos
@pytest.fixture(scope="module")
def conn():
    # Lee las credenciales desde variables de entorno
    server   = os.environ.get("SERVER", "")
    database = os.environ.get("DATABASE", "")
    user     = os.environ.get("USER", "")
    pwd      = os.environ.get("PWD", "")

    conn = get_sqlserver_conn(
        server=server,
        database=database,
        user=user,
        pwd=pwd
    )
    cur = conn.cursor()
    # Asegura esquema y tabla
    cur.execute("""
    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'Sales')
        EXEC('CREATE SCHEMA Sales');
    IF OBJECT_ID('Sales.Orders', 'U') IS NULL
        CREATE TABLE Sales.Orders (
            OrderID INT IDENTITY PRIMARY KEY,
            CustomerName NVARCHAR(100),
            Amount DECIMAL(10,2),
            OrderDate DATETIME2
        );
    DELETE FROM Sales.Orders;
    INSERT INTO Sales.Orders (CustomerName, Amount, OrderDate)
    VALUES ('Test1',100.00,GETDATE()),('Test2',50.50,GETDATE());
    """)
    conn.commit()
    yield conn
    conn.close()

def test_get_sqlserver_conn(conn):
    # La conexión no debe ser None y debe permitir cursor()
    assert conn is not None
    cur = conn.cursor()
    assert hasattr(cur, 'execute')

def test_load_table_returns_dataframe(conn):
    # Carga exactamente dos filas y las columnas esperadas
    df = load_table(conn, 'Sales.Orders', top_n=2)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    for col in ['OrderID', 'CustomerName', 'Amount', 'OrderDate']:
        assert col in df.columns

