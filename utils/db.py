# utils/db.py

import pandas as pd
import pyodbc

def get_sqlserver_conn(server: str, database: str, user: str, pwd: str):
    """
    Obtiene una conexión ODBC a SQL Server.
    Para entornos locales (Docker) con self-signed certs,
    desactivamos encriptación y confiamos en el certificado:
    """
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={pwd};"
        f"Encrypt=no;"                    # deshabilita encriptación SSL
        f"TrustServerCertificate=yes"     # confía en el certificado del servidor
    )
    return pyodbc.connect(conn_str)

def load_table(conn, table_name: str, top_n: int = None) -> pd.DataFrame:
    """
    Carga una tabla en un DataFrame de pandas.
    Si se pasa top_n, añade un TOP a la consulta.
    """
    top_clause = f"TOP {top_n} " if top_n else ""
    sql = f"SELECT {top_clause}* FROM {table_name}"
    return pd.read_sql(sql, conn)
