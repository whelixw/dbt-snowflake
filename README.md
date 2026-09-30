# dbt + Snowflake starter

A small dbt project wired for Snowflake. It includes a placeholder customer seed,
a cleaned staging model, a customer dimension, and basic data tests.

## Local setup

1. Create and activate a Python virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `profiles.example.yml` to `~/.dbt/profiles.yml`.
4. Set the Snowflake environment variables referenced by the profile.
5. Validate the connection with `dbt debug`.

## Build

```sh
dbt seed
dbt build
```

The seed is created in a schema suffixed with `_RAW`; staging and mart models
are built in the target schema configured in your dbt profile.
