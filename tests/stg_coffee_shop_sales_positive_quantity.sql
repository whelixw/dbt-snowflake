-- A singular dbt test passes when this query returns no rows.
select transaction_id, transaction_qty
from {{ ref('stg_coffee_shop_sales') }}
where transaction_qty <= 0
