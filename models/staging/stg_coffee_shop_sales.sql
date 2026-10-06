{{ config(materialized='table') }}

select
    *,
    month(transaction_date) as transaction_month,
    dayname(transaction_date) as transaction_weekday,
	hour(to_time(transaction_time, 'HH24:MI:SS')) as transaction_hour
from {{ ref('coffee_shop_sales_n3000') }}