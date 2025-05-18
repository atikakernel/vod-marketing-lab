    -- models/intermediate/int_daily_sales_summary.sql

    -- Este modelo calcula el total de ventas y el número de órdenes por día.
    -- Utiliza la función ref() para depender del modelo stg_orders.

    SELECT
        CAST(OrderDate AS DATE) AS order_day,  -- Extrae solo la fecha, sin la hora
        COUNT(OrderID) AS total_orders,
        SUM(Amount) AS total_sales_amount
    FROM {{ ref('stg_orders') }} -- Referencia a tu modelo de staging stg_orders.sql
    GROUP BY
        CAST(OrderDate AS DATE)
    -- NO ORDER BY clause here for a view
    