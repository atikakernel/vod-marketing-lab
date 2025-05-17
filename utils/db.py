import os
import pyodbc
import pandas as pd

def get_sqlserver_conn(server: str, database: str, user: str, pwd: str):
    """
    Obtiene una conexión ODBC a SQL Server.
    Ajusta las opciones de encriptación y timeout para Azure SQL.
    """
    is_azure_sql = ".database.windows.net" in server.lower()
    
    encrypt_option = "yes" if is_azure_sql else "no"
    trust_cert_option = "no" if is_azure_sql else "yes" 
    
    conn_str_parts = [
        "DRIVER={ODBC Driver 18 for SQL Server};",
        f"SERVER={server};",
        f"DATABASE={database};",
        f"UID={user};",
        f"PWD={pwd};", # Pytest enmascara esto en los logs, pero la variable se pasa.
        f"Encrypt={encrypt_option};",
        f"TrustServerCertificate={trust_cert_option};"
    ]

    timeout_str_part = ""
    if is_azure_sql:
        timeout_str_part = "Connection Timeout=30;"
        conn_str_parts.append(timeout_str_part)
        # Considera también 'MARS_Connection=yes;' si usas Multiple Active Result Sets

    conn_str = "".join(conn_str_parts)
    
    # --- LÍNEA DE DEPURACIÓN IMPORTANTE ---
    # Construye la cadena para el print sin la contraseña
    debug_conn_str_parts = [
        "DRIVER={ODBC Driver 18 for SQL Server};",
        f"SERVER={server};",
        f"DATABASE={database};",
        f"UID={user};",
        "PWD=********;", # Contraseña ofuscada
        f"Encrypt={encrypt_option};",
        f"TrustServerCertificate={trust_cert_option};"
    ]
    if is_azure_sql:
        debug_conn_str_parts.append(timeout_str_part)
    
    print(f"DEBUG utils.db: Cadena de conexión construida: {''.join(debug_conn_str_parts)}")
    # --- FIN LÍNEA DE DEPURACIÓN ---

    return pyodbc.connect(conn_str)

def load_table(conn, table_name: str, top_n: int = None) -> pd.DataFrame:
    """
    Carga una tabla en un DataFrame de pandas.
    Si se pasa top_n, añade un TOP a la consulta.
    """
    top_clause = f"TOP {top_n} " if top_n else ""
    sql = f"SELECT {top_clause}* FROM {table_name}"
    return pd.read_sql(sql, conn)
