-- Null prices are covered separately by the column's not_null test.
select transaction_id, unit_price
from {{ ref('stg_coffee_shop_sales') }}
where unit_price < 0
