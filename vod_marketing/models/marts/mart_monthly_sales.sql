    -- models/marts/mart_monthly_sales.sql

    -- Este modelo calcula el total de ventas y el número de órdenes por mes.
    -- Utiliza la función ref() para depender del modelo int_daily_sales_summary.

    SELECT
        FORMAT(order_day, 'yyyy-MM') AS sales_year_month, -- Formatea la fecha como 'AAAA-MM'
        SUM(total_orders) AS total_monthly_orders,
        SUM(total_sales_amount) AS total_monthly_sales
    FROM {{ ref('int_daily_sales_summary') }} -- Referencia a tu modelo intermedio
    GROUP BY
        FORMAT(order_day, 'yyyy-MM')
    -- NO ORDER BY clause here for a view
    