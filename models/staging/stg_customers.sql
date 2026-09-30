with source as (
    select * from {{ ref('raw_customers') }}
),

renamed as (
    select
        customer_id,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        lower(email) as email,
        signup_date,
        lower(status) as status
    from source
)

select * from renamed
