select
    store_id,
    count(*) as order_count,
	sum(transaction_qty) as total_amount,
    sum(transaction_qty * unit_price) as total_revenue
from {{ ref('coffee_shop_sales_n3000') }}
group by store_id