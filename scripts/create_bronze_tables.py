#!/usr/bin/env python3
import os, sys

# Inserta la carpeta padre (la raíz del proyecto) en sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.db import get_sqlserver_conn


# Lee credenciales de las env vars
SERVER   = os.environ['AZURE_SQL_SERVER']
DATABASE = os.environ['AZURE_SQL_DATABASE']
USER     = os.environ['AZURE_SQL_USER']
PWD      = os.environ['AZURE_SQL_PASSWORD']

DDL = """
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'bronze')
  EXEC('CREATE SCHEMA bronze;');

CREATE TABLE IF NOT EXISTS bronze.sales_orders (
  order_id    INT            NOT NULL PRIMARY KEY,
  article     NVARCHAR(200)  NULL,
  price       DECIMAL(10,2)  NULL,
  quantity    INT            NULL,
  customer_id INT            NULL,
  campaign_id INT            NULL,
  created_at  DATETIME2      DEFAULT SYSUTCDATETIME(),
  source_file NVARCHAR(255)  DEFAULT 'landing/…',
  load_batch  INT            NULL
);

CREATE TABLE IF NOT EXISTS bronze.customers (
  customer_id INT            NOT NULL PRIMARY KEY,
  name        NVARCHAR(200)  NULL,
  email       NVARCHAR(200)  NULL,
  phone       NVARCHAR(50)   NULL,
  order_id    INT            NULL,
  campaign_id INT            NULL,
  created_at  DATETIME2      DEFAULT SYSUTCDATETIME(),
  source_file NVARCHAR(255)  DEFAULT 'landing/…',
  load_batch  INT            NULL
);

CREATE TABLE IF NOT EXISTS bronze.marketing_campaigns (
  campaign_id INT            NOT NULL PRIMARY KEY,
  name        NVARCHAR(200)  NULL,
  order_id    INT            NULL,
  customer_id INT            NULL,
  created_at  DATETIME2      DEFAULT SYSUTCDATETIME(),
  source_file NVARCHAR(255)  DEFAULT 'landing/…',
  load_batch  INT            NULL
);

ALTER TABLE bronze.sales_orders
  ADD CONSTRAINT fk_sales_orders_customers
    FOREIGN KEY(customer_id)
    REFERENCES bronze.customers(customer_id);

ALTER TABLE bronze.sales_orders
  ADD CONSTRAINT fk_sales_orders_campaigns
    FOREIGN KEY(campaign_id)
    REFERENCES bronze.marketing_campaigns(campaign_id);
"""

def main():
    conn = get_sqlserver_conn(SERVER, DATABASE, USER, PWD)
    cur  = conn.cursor()
    for stmt in DDL.split(';'):
        if stmt.strip():
            cur.execute(stmt)
    conn.commit()
    cur.close()
    print("Schema y tablas bronze aseguradas.")

if __name__ == "__main__":
    main()
