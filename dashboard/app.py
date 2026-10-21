from pathlib import Path
import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Coffee Shop Sales", page_icon="☕", layout="wide")

STORE_COLORS = {
    "Astoria": "#368A83",
    "Hell's Kitchen": "#CD7952",
    "Lower Manhattan": "#8174A8",
}
CATEGORY_COLORS = {
    "Bakery": "#C98A46",
    "Branded": "#8C738D",
    "Coffee": "#85583E",
    "Coffee beans": "#A87657",
    "Drinking Chocolate": "#B66873",
    "Flavours": "#CF9B45",
    "Loose Tea": "#8B9B52",
    "Packaged Chocolate": "#9B6B72",
    "Tea": "#368A83",
}


def color_scale(palette):
    return alt.Scale(domain=list(palette), range=list(palette.values()))


def chart_style(chart):
    return chart.configure_view(strokeWidth=0).configure_axis(
        gridColor="#888888", gridOpacity=0.12, domain=False, tickSize=0,
        labelPadding=8, titlePadding=12,
    )

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
    daily_data = daily.rename("revenue").reset_index()
    daily_base = alt.Chart(daily_data).encode(
        x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%d %b")),
        y=alt.Y("revenue:Q", title="Revenue", axis=alt.Axis(format=",.0f")),
        tooltip=[alt.Tooltip("Date:T", title="Date", format="%d %b %Y"),
                 alt.Tooltip("revenue:Q", title="Revenue", format=",.2f")],
    )
    daily_chart = daily_base.mark_area(color="#CD7952", opacity=0.15) + daily_base.mark_line(color="#CD7952", strokeWidth=2.5)
    st.altair_chart(chart_style(daily_chart.properties(height=280)), width="stretch")
    left, right = st.columns(2)
    with left:
        st.subheader("Revenue by store")
        store_data = filtered.groupby("store_location", as_index=False).revenue.sum()
        store_chart = alt.Chart(store_data).mark_bar(cornerRadiusEnd=5).encode(
            x=alt.X("revenue:Q", title="Revenue", axis=alt.Axis(format=",.0f")),
            y=alt.Y("store_location:N", title=None, sort="-x"),
            color=alt.Color("store_location:N", scale=color_scale(STORE_COLORS), legend=None),
            tooltip=[alt.Tooltip("store_location:N", title="Store"),
                     alt.Tooltip("revenue:Q", title="Revenue", format=",.2f")],
        )
        st.altair_chart(chart_style(store_chart.properties(height=240)), width="stretch")
    with right:
        st.subheader("Revenue by hour")
        hourly = filtered.groupby(["hour", "store_location"]).revenue.sum()
        hour_index = pd.MultiIndex.from_product(
            [range(24), sorted(filtered.store_location.unique())],
            names=["hour", "store_location"],
        )
        hourly = hourly.reindex(hour_index, fill_value=0).rename("revenue").reset_index()
        hour_chart = alt.Chart(hourly).mark_bar().encode(
            x=alt.X("hour:O", title="Hour of day", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("revenue:Q", title="Revenue", axis=alt.Axis(format=",.0f")),
            color=alt.Color("store_location:N", title="Store", scale=color_scale(STORE_COLORS),
                            legend=alt.Legend(orient="bottom")),
            tooltip=[alt.Tooltip("hour:O", title="Hour"),
                     alt.Tooltip("store_location:N", title="Store"),
                     alt.Tooltip("revenue:Q", title="Revenue", format=",.2f")],
        )
        st.altair_chart(chart_style(hour_chart.properties(height=240)), width="stretch")
with details:
    st.subheader("Revenue by product category")
    category_data = filtered.groupby("product_category", as_index=False).revenue.sum()
    category_chart = alt.Chart(category_data).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("revenue:Q", title="Revenue", axis=alt.Axis(format=",.0f")),
        y=alt.Y("product_category:N", title=None, sort="-x"),
        color=alt.Color("product_category:N", scale=color_scale(CATEGORY_COLORS), legend=None),
        tooltip=[alt.Tooltip("product_category:N", title="Category"),
                 alt.Tooltip("revenue:Q", title="Revenue", format=",.2f")],
    )
    st.altair_chart(chart_style(category_chart.properties(height=320)), width="stretch")
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

