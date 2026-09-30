select
    customer_id,
    first_name,
    last_name,
    first_name || ' ' || last_name as full_name,
    email,
    signup_date,
    status,
    status = 'active' as is_active
from {{ ref('stg_customers') }}
