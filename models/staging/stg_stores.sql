{{ config(materialized='table') }}

select distinct 
	store_id, 
	store_location
from {{ ref('stg_coffee_shop_sales') }}
order by store_id