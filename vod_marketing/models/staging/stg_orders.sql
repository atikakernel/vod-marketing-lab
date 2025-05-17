    -- Este es tu primer modelo dbt.
    -- Selecciona todos los datos de la tabla fuente 'Orders'.
    -- La función `source()` le dice a dbt que busque una fuente definida
    -- en tus archivos .yml.

    SELECT
        OrderID,
        CustomerName,
        Amount,
        OrderDate
        -- Puedes añadir transformaciones aquí si quieres, por ejemplo:
        -- , Amount * 0.05 AS tax_amount -- Calcula un impuesto
        -- , UPPER(CustomerName) AS customer_name_uppercase -- Convierte a mayúsculas
    FROM {{ source('tienda_fuente', 'Orders') }} 
    -- 'tienda_fuente' es el 'name' del source que definiste en stg_sources.yml
    -- 'Orders' es el 'name' de la tabla dentro de ese source.

    -- Opcional: Puedes añadir un WHERE clause si quieres filtrar
    -- WHERE Amount > 0 
    