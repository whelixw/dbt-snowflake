select
    store_id,
	transaction_hour,
    count(*) as order_count,
	sum(transaction_qty) as total_amount,
    sum(transaction_qty * unit_price) as total_revenue
from {{ ref('stg_coffee_shop_sales') }}
group by store_id, transaction_hour
order by transaction_hour