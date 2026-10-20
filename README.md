# Coffee shop analytics

A dbt + Snowflake learning project with a portable Streamlit dashboard.

## Run the dashboard

From the repository root, with Python 3.10 or newer:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r dashboard/requirements.txt
.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

The dashboard defaults to **Saved demo**, reading `dashboard/data/fct_coffee_shop_sales.csv`: actual results exported from the Snowflake dbt reporting model. This mode needs no credentials, database connection, or dbt installation and continues to work after the Snowflake trial expires. **Live Snowflake** queries the same reporting model using your local connection settings and a masked password plus authenticator code (`username_password_mfa`).

Features: store, category, and date filters; revenue, orders, units sold, and average order value; daily and hourly charts; store and category comparisons; top products; and filtered CSV downloads.

Revenue = quantity × unit price. Orders count source rows, matching `store_order_totals.sql`. Currency is unspecified. The snapshot covers January–June 2023 with 149,116 sales rows, 214,470 units, and 698,812.33 revenue. Both modes calculate dashboard summaries with pandas from the reporting model results. Snapshot provenance and verification totals are recorded in [dashboard/data/readme.md](dashboard/data/readme.md).

## Share a hosted demo from GitHub

GitHub stores the code and sample data; a Streamlit server runs the interactive app. GitHub Pages cannot run this Python app.

1. Push the repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and create an app.
3. Select your repository and branch, with `dashboard/app.py` as the entrypoint.
4. Deploy and share the generated URL. Saved demo needs no Snowflake secrets. Live Snowflake additionally requires local or hosted connection settings; never commit credentials.

Community Cloud finds `dashboard/requirements.txt` beside the entrypoint, keeping dashboard dependencies separate from the root dbt dependencies. See the [deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Run dbt with Snowflake

Install the root `requirements.txt`, configure your local dbt profile using `profiles.example.yml`, and set its `DBT_SNOWFLAKE_*` environment variables. Run:

```powershell
dbt seed
dbt run
dbt test
```

These commands require an active Snowflake account. Saved demo is independent of that pipeline. Live Snowflake reads `fct_coffee_shop_sales`, defined in `models/marts/fct_coffee_shop_sales.sql`. The full source dataset is `seeds/coffee_shop_sales_full.csv`. Keep connection settings in the ignored `.streamlit/secrets.toml`; password and authenticator code are entered in the app.
