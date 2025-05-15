# utils/db.py

import pandas as pd
import pyodbc

def get_sqlserver_conn(server: str, database: str, user: str, pwd: str):
    # ...
    is_azure_sql = ".database.windows.net" in server.lower()
    
    encrypt_option = "yes" if is_azure_sql else "no"
    trust_cert_option = "no" if is_azure_sql else "yes" # Para Azure, confía en el certificado del sistema

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={pwd};"
        f"Encrypt={encrypt_option};"
        f"TrustServerCertificate={trust_cert_option};"
        # Podrías necesitar "Connection Timeout=30;" para conexiones a Azure
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
