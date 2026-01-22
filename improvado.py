import streamlit as st
import pandas as pd

# --------------------
# Page config
# --------------------
st.set_page_config(
    page_title="Marketing Performance Dashboard",
    layout="wide"
)

st.title("Marketing Performance Dashboard")

# --------------------
# Load data
# --------------------

url = 'https://raw.githubusercontent.com/eugenio9445/mkt_test/refs/heads/main/2026-01-21%205_28pm_2026-01-21-1915.csv'
df = pd.read_csv(url)
df.columns = df.columns.str.upper()
df["FECHA"] = pd.to_datetime(df["FECHA"])


# --------------------
# Sidebar filters
# --------------------
st.sidebar.header("Filters")

date_range = st.sidebar.date_input(
    "Date range",
    [df["FECHA"].min(), df["FECHA"].max()]
)

platform_map = {
     1:"facebook",
     2:"google":,
     3:"tiktok"
}

df["PLATAFORMA"] = df["PLATAFORMA"].str.lower().map(platform_map)

platforms = st.sidebar.multiselect(
    "Platform",
    options=sorted(df["PLATAFORMA"].unique()),
    default=sorted(df["PLATAFORMA"].unique())
)

campaigns = st.sidebar.multiselect(
    "Campaign",
    options=sorted(df["CAMPAIGN_NAME"].unique()),
    default=sorted(df["CAMPAIGN_NAME"].unique())
)

# --------------------
# Apply filters
# --------------------
filtered_df = df[
    (df["FECHA"].dt.date >= date_range[0]) &
    (df["FECHA"].dt.date <= date_range[1]) &
    (df["PLATAFORMA"].isin(platforms)) &
    (df["CAMPAIGN_NAME"].isin(campaigns))
]

# --------------------
# KPI calculations
# --------------------
total_impressions = filtered_df["IMPRESSIONS"].sum()
total_clicks = filtered_df["CLICKS"].sum()
total_cost = filtered_df["COST"].sum()
total_conversions = filtered_df["CONVERSIONS"].sum()

ctr = (total_clicks / total_impressions) * 100 if total_impressions else 0
cpc = total_cost / total_clicks if total_clicks else 0

# --------------------
# KPI section
# --------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Impressions", f"{total_impressions:,}")
col2.metric("Clicks", f"{total_clicks:,}")
col3.metric("Cost", f"${total_cost:,.2f}")
col4.metric("Conversions", f"{total_conversions:,}")
col5.metric("CTR", f"{ctr:.2f}%")
col6.metric("CPC", f"${cpc:.2f}")

st.divider()

# --------------------
# Time series chart
# --------------------
st.subheader("📈 Performance Over Time")

daily_df = (
    filtered_df
    .groupby("FECHA", as_index=False)
    .agg({
        "IMPRESSIONS": "sum",
        "CLICKS": "sum",
        "COST": "sum",
        "CONVERSIONS": "sum"
    })
)

metric = st.selectbox(
    "Select metric",
    ["IMPRESSIONS", "CLICKS", "COST", "CONVERSIONS"]
)

st.line_chart(
    daily_df.set_index("FECHA")[metric]
)

# --------------------
# Campaign performance table
# --------------------
st.subheader("🎯 Campaign Performance")

campaign_table = (
    filtered_df
    .groupby("CAMPAIGN_NAME", as_index=False)
    .agg({
        "IMPRESSIONS": "sum",
        "CLICKS": "sum",
        "COST": "sum",
        "CONVERSIONS": "sum"
    })
)

campaign_table["CTR (%)"] = (
    campaign_table["CLICKS"] / campaign_table["IMPRESSIONS"] * 100
).round(2)

campaign_table["CPC"] = (
    campaign_table["COST"] / campaign_table["CLICKS"]
).round(2)

st.dataframe(
    campaign_table.sort_values("CONVERSIONS", ascending=False),
    use_container_width=True
)
     









