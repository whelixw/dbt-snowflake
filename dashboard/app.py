from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Coffee Shop Sales", page_icon="☕", layout="wide")

@st.cache_data
def load_sales():
    data = pd.read_csv(Path(__file__).resolve().parents[1] / "seeds" / "coffee_shop_sales_n3000.csv", parse_dates=["transaction_date"])
    data["revenue"] = data["transaction_qty"] * data["unit_price"]
    data["hour"] = pd.to_datetime(data["transaction_time"], format="%H:%M:%S").dt.hour
    return data

sales = load_sales()
st.title("☕ Coffee Shop Sales")
st.caption("Explore the repository's coffee shop sample. No Snowflake account required.")
with st.sidebar:
    st.header("Explore sales")
    stores = st.multiselect("Stores", sorted(sales.store_location.unique()), default=sorted(sales.store_location.unique()), key="stores")
    categories = st.multiselect("Product categories", sorted(sales.product_category.unique()), default=sorted(sales.product_category.unique()), key="categories")
    first, last = sales.transaction_date.min().date(), sales.transaction_date.max().date()
    dates = st.date_input("Date range", (first, last), min_value=first, max_value=last, key="dates")
    st.caption(f"Sample coverage: {first:%d %b %Y} – {last:%d %b %Y} · {len(sales):,} rows")
    st.button("Reset filters", on_click=lambda: st.session_state.clear())
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
    st.write("This dashboard reads the committed coffee shop CSV and calculates summaries with pandas. It mirrors the revenue and order definitions in the dbt store totals models, but does not query Snowflake or execute dbt. The limited sample keeps the demo reproducible after the Snowflake trial ends.")

