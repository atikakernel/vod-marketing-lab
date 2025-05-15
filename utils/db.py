import os
import pandas as pd
import pyodbc

def get_sqlserver_conn(server: str, database: str, user: str, pwd: str):
    """
    Obtiene una conexión ODBC a SQL Server, con cifrado desactivado y certificado de servidor de confianza
    (necesario para contenedores locales con self-signed certs).
    """
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={pwd};"
        # ↓ estas dos opciones permiten la conexión sin certificado válido
        f"Encrypt=no;"
        f"TrustServerCertificate=yes"
    )
    return pyodbc.connect(conn_str)


def load_table(conn, table_name: str, top_n: int = None) -> pd.DataFrame:
    """
    Carga una tabla de SQL Server en un pandas.DataFrame.
    Si top_n está presente, limita el número de filas.
    """
    sql = f"SELECT {'TOP ' + str(top_n) if top_n else ''} * FROM {table_name}"
    return pd.read_sql(sql, conn)
