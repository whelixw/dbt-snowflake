select
    store_id,
    count(*) as order_count,
	sum(transaction_qty) as total_amount,
    sum(revenue) as total_revenue
from {{ ref('fct_coffee_shop_sales') }}
group by store_id
