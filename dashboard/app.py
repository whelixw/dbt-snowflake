from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Coffee Shop Sales", page_icon="☕", layout="wide")

def prepare_sales(data):
    data = data.copy()
    data.columns = data.columns.str.lower()
    data["transaction_date"] = pd.to_datetime(data["transaction_date"])
    data["hour"] = data["transaction_hour"]
    return data


@st.cache_data
def load_saved_sales():
    csv_path = Path(__file__).resolve().parent / "data" / "fct_coffee_shop_sales.csv"
    return prepare_sales(pd.read_csv(csv_path))


def load_live_sales():
    with st.sidebar.form("snowflake_login"):
        password = st.text_input("Snowflake password", type="password")
        passcode = st.text_input("Authenticator code", type="password")
        submitted = st.form_submit_button("Connect")

    if not submitted:
        st.info("Enter your password and current authenticator code, then select Connect.")
        st.stop()
    if not password or not passcode.strip():
        st.info("Both your password and authenticator code are required.")
        st.stop()

    try:
        conn = st.connection(
            "snowflake",
            authenticator="username_password_mfa",
            password=password,
            passcode=passcode.strip(),
        )
        data = conn.query("select * from fct_coffee_shop_sales", ttl=300)
    except Exception:
        st.error("Could not load Snowflake data. Check your local connection settings and credentials, or use Saved demo.")
        st.stop()

    return prepare_sales(data)


def reset_filters():
    for key in ("stores", "categories", "dates"):
        st.session_state.pop(key, None)


def change_source():
    reset_filters()
    st.session_state.pop("live_sales", None)


st.title("☕ Coffee Shop Sales")
source = st.sidebar.radio(
    "Data source",
    ["Saved demo", "Live Snowflake"],
    key="data_source",
    on_change=change_source,
)
if source == "Saved demo":
    sales = load_saved_sales()
    st.caption("Saved demo · Snowflake snapshot exported 20 Oct 2026 · dbt model: fct_coffee_shop_sales")
else:
    st.caption("Live Snowflake data · dbt model: fct_coffee_shop_sales")
    if "live_sales" not in st.session_state:
        st.session_state["live_sales"] = load_live_sales()
    sales = st.session_state["live_sales"]
    st.sidebar.caption("Connected. Data stays loaded while you explore. Switch modes to reconnect.")

with st.sidebar:
    st.header("Explore sales")
    stores = st.multiselect("Stores", sorted(sales.store_location.unique()), default=sorted(sales.store_location.unique()), key="stores")
    categories = st.multiselect("Product categories", sorted(sales.product_category.unique()), default=sorted(sales.product_category.unique()), key="categories")
    first, last = sales.transaction_date.min().date(), sales.transaction_date.max().date()
    dates = st.date_input("Date range", (first, last), min_value=first, max_value=last, key="dates")
    st.caption(f"Data coverage: {first:%d %b %Y} – {last:%d %b %Y} · {len(sales):,} rows")
    st.button("Reset filters", on_click=reset_filters)
if len(dates) != 2:
    st.info("Choose both a start and an end date.")
    st.stop()
filtered = sales.loc[sales.store_location.isin(stores) & sales.product_category.isin(categories) & sales.transaction_date.between(pd.Timestamp(dates[0]), pd.Timestamp(dates[1]))].copy()
if filtered.empty:
    st.info("No sales match these filters. Select another store, category, or date range.")
    st.stop()
revenue = filtered.revenue.sum()
a, b, c, d = st.columns(4)
a.metric("Revenue", f"{revenue:,.2f}")
b.metric("Orders", f"{len(filtered):,}")
c.metric("Units sold", f"{filtered.transaction_qty.sum():,}")
d.metric("Average order value", f"{revenue / len(filtered):,.2f}")
st.caption("Orders count source rows, matching the dbt store totals model. Revenue = quantity × unit price. The source does not specify a currency.")
overview, details = st.tabs(["Sales overview", "Products & data"])
with overview:
    st.subheader("Daily revenue")
    daily = filtered.groupby("transaction_date").revenue.sum().reindex(pd.date_range(dates[0], dates[1]), fill_value=0)
    daily.index.name = "Date"
    st.line_chart(daily)
    left, right = st.columns(2)
    with left:
        st.subheader("Revenue by store")
        st.bar_chart(filtered.groupby("store_location").revenue.sum())
    with right:
        st.subheader("Revenue by hour")
        st.bar_chart(filtered.groupby("hour").revenue.sum().reindex(range(24), fill_value=0))
with details:
    st.subheader("Revenue by product category")
    st.bar_chart(filtered.groupby("product_category").revenue.sum())
    st.subheader("Top 10 products")
    products = filtered.groupby("product_detail").agg(units=("transaction_qty", "sum"), revenue=("revenue", "sum")).sort_values("revenue", ascending=False).head(10)
    st.dataframe(products, width="stretch")
    st.subheader("Filtered transactions")
    export = filtered.drop(columns="hour")
    st.dataframe(export, hide_index=True, width="stretch")
    st.download_button("Download filtered sales", export.to_csv(index=False).encode("utf-8"), "coffee_shop_sales.csv", "text/csv")
with st.expander("About this demo"):
    st.write("Both modes use the fct_coffee_shop_sales reporting model and calculate dashboard summaries with pandas. Revenue = quantity × unit price; orders count sales rows.")
    if source == "Saved demo":
        st.write("Saved demo reads a local CSV exported from Snowflake on 20 October 2026. The verified snapshot contains 149,116 sales rows covering January–June 2023. This mode requires no credentials or Snowflake connection and remains usable after the trial ends.")
    else:
        st.write("Live Snowflake queries fct_coffee_shop_sales using your local connection settings and password plus authenticator code. Results stay in this session while you explore; switch modes to reconnect. This dashboard does not run dbt.")

