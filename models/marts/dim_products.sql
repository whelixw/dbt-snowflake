{{ config(materialized='table') }}

select distinct 
	product_id, 
	product_category, 
	product_type, 
	product_detail
from {{ ref('stg_coffee_shop_sales') }}
