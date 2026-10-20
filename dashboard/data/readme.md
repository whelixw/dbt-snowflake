# Saved demo data

Source: Snowflake reporting model `fct_coffee_shop_sales`
dbt model: `models/marts/fct_coffee_shop_sales.sql`
Snapshot exported and verified: 2026-10-20
CSV: `fct_coffee_shop_sales.csv`

This snapshot contains the actual reporting model results exported from
Snowflake, with the original column names preserved.

Verified against Snowflake:
- Sales rows: 149,116
- Total quantity: 214,470
- Total revenue: 698,812.33
- First sale date: 2023-01-01
- Last sale date: 2023-06-30

Revenue is calculated as transaction_qty × unit_price.