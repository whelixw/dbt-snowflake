{{ config(materialized='table') }}

select
    transaction_id,
    transaction_date,
    transaction_time,
    transaction_hour,
    store_id,
    store_location,
    product_id,
    product_category,
    product_type,
    product_detail,
    transaction_qty,
    unit_price,
    transaction_qty * unit_price as revenue
from {{ ref('stg_coffee_shop_sales') }}