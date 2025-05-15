import os
import pyodbc
import pandas as pd # pandas no se usa en get_sqlserver_conn pero sí en load_table

def get_sqlserver_conn(server: str, database: str, user: str, pwd: str):
    """
    Obtiene una conexión ODBC a SQL Server.
    Ajusta las opciones de encriptación y timeout para Azure SQL.
    """
    is_azure_sql = ".database.windows.net" in server.lower()
    
    encrypt_option = "yes" if is_azure_sql else "no"
    # Para Azure SQL, no confíes ciegamente en el certificado del servidor si no es necesario;
    # el driver debería usar el trust store del sistema. 'no' es más seguro para Azure.
    # Para Docker local con cert autofirmado, sí es necesario confiar ('yes').
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

    # Añadir Connection Timeout solo para Azure SQL
    if is_azure_sql:
        conn_str_parts.append("Connection Timeout=30;")
        # Considera también 'MARS_Connection=yes;' si usas Multiple Active Result Sets

    conn_str = "".join(conn_str_parts)
    
    # Para depuración, puedes imprimir la cadena de conexión (sin la contraseña)
    # print(f"DEBUG: Connection String: DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={user};PWD=********;Encrypt={encrypt_option};TrustServerCertificate={trust_cert_option};{'Connection Timeout=30;' if is_azure_sql else ''}")

    return pyodbc.connect(conn_str)

def load_table(conn, table_name: str, top_n: int = None) -> pd.DataFrame:
    """
    Carga una tabla en un DataFrame de pandas.
    Si se pasa top_n, añade un TOP a la consulta.
    """
    top_clause = f"TOP {top_n} " if top_n else ""
    sql = f"SELECT {top_clause}* FROM {table_name}"
    return pd.read_sql(sql, conn)
