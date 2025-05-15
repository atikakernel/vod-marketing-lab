import os
import pytest
import pandas as pd
from utils.db import get_sqlserver_conn, load_table

# --- CREDENCIALES DESDE ENTORNO ----------------------
server   = os.getenv("SERVER",   "vod-marketing-server.database.windows.net")
database = os.getenv("DATABASE", "vod_marketing_db")
user     = os.getenv("DB_USER",  "dbadmin")
pwd      = os.getenv("DB_PWD",   "@Infernity1")
# ------------------------------------------------------

@pytest.fixture(scope="module")
def conn():
    conn = get_sqlserver_conn(server, database, user, pwd)
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
    assert conn is not None
    cur = conn.cursor()
    assert hasattr(cur, 'execute')

def test_load_table_returns_dataframe(conn):
    df = load_table(conn, 'Sales.Orders', top_n=2)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    for col in ['OrderID', 'CustomerName', 'Amount', 'OrderDate']:
        assert col in df.columns
