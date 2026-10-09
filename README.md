# Coffee shop analytics

A dbt + Snowflake learning project with a portable Streamlit dashboard.

## Run the dashboard

From the repository root, with Python 3.10 or newer:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r dashboard/requirements.txt
.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

The dashboard reads the committed `seeds/coffee_shop_sales_n3000.csv` sample. No credentials, running database, or dbt installation are needed. It continues to work after your Snowflake trial expires.

Features: store, category, and date filters; revenue, orders, units sold, and average order value; daily and hourly charts; store and category comparisons; top products; and filtered CSV downloads.

Revenue = quantity × unit price. Orders count source rows, matching `store_order_totals.sql`. Currency is unspecified. This is a limited sample, not a full trading history. Dashboard summaries are computed with pandas rather than read from materialized dbt models.

## Share a hosted demo from GitHub

GitHub stores the code and sample data; a Streamlit server runs the interactive app. GitHub Pages cannot run this Python app.

1. Push the repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and create an app.
3. Select your repository and branch, with `dashboard/app.py` as the entrypoint.
4. Deploy and share the generated URL. No Snowflake secrets are needed.

Community Cloud finds `dashboard/requirements.txt` beside the entrypoint, keeping dashboard dependencies separate from the root dbt dependencies. See the [deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Run dbt with Snowflake

Install the root `requirements.txt`, configure your local dbt profile using `profiles.example.yml`, and set its `DBT_SNOWFLAKE_*` environment variables. Run:

```powershell
dbt seed
dbt run
dbt test
```

These commands require an active Snowflake account. The Streamlit demo is independent of that pipeline. A future live-data version can query the dbt models while retaining this sample mode.
