{{ config(materialized='table') }}

with cleaned as (
    select
        cast(transaction_id as integer) as transaction_id,
        cast(transaction_date as date) as transaction_date,
        to_time(transaction_time, 'HH24:MI:SS') as transaction_time,
        cast(transaction_qty as integer) as transaction_qty,
        cast(store_id as integer) as store_id,
        trim(cast(store_location as varchar)) as store_location,
        cast(product_id as integer) as product_id,
        cast(unit_price as number(10, 2)) as unit_price,
        trim(cast(product_category as varchar)) as product_category,
        trim(cast(product_type as varchar)) as product_type,
        trim(cast(product_detail as varchar)) as product_detail
    from {{ ref('coffee_shop_sales_full') }}
)

select
    transaction_id,
    transaction_date,
    transaction_time,
    transaction_qty,
    store_id,
    store_location,
    product_id,
    unit_price,
    product_category,
    product_type,
    product_detail,
    month(transaction_date) as transaction_month,
    dayname(transaction_date) as transaction_weekday,
    hour(transaction_time) as transaction_hour
from cleaned
