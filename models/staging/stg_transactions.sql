{{ config(materialized='table') }}

select distinct 
	transaction_id,
	transaction_date,
	transaction_time, 
	transaction_qty, 
	store_id, 
	product_id, 
	unit_price
from {{ ref('stg_coffee_shop_sales') }}
order by transaction_id