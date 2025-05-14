import pyodbc
import pandas as pd

def get_sqlserver_conn(server, database, user, pwd):
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={user};PWD={pwd}"
    return pyodbc.connect(conn_str)

def load_table(conn, table_name, top_n: int = 100):
    """
  Carga las primeras top_n filas de la tabla en un DataFrame.
   """
    query = f"SELECT TOP {top_n} * FROM {table_name}"
    return pd.read_sql(query, conn)

