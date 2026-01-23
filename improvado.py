import streamlit as st
import pandas as pd
import altair as alt


st.set_page_config(
    page_title="Marketing Performance Dashboard",
    layout="wide"
)

st.title("Marketing Performance Dashboard")

url = "https://raw.githubusercontent.com/eugenio9445/mkt_test/refs/heads/main/2026-01-21%205_28pm_2026-01-21-1915.csv"
df = pd.read_csv(url)

df.columns = df.columns.str.upper()
df["FECHA"] = pd.to_datetime(df["FECHA"])

platform_map = {
    1: "facebook",
    2: "google",
    3: "tiktok"
}
df["PLATAFORMA"] = df["PLATAFORMA"].map(platform_map)

st.sidebar.header("Filters")

date_range = st.sidebar.date_input(
    "Date range",
    value=[df["FECHA"].min(), df["FECHA"].max()]
)

date_filtered_df = df[
    (df["FECHA"].dt.date >= date_range[0]) &
    (df["FECHA"].dt.date <= date_range[1])
]


platforms = st.sidebar.multiselect(
    "Platform",
    options=sorted(date_filtered_df["PLATAFORMA"].dropna().unique()),
    default=sorted(date_filtered_df["PLATAFORMA"].dropna().unique())
)

platform_filtered_df = date_filtered_df[
    date_filtered_df["PLATAFORMA"].isin(platforms)
]

groups = st.sidebar.multiselect(
    "Group",
    options=sorted(platform_filtered_df["GROUP_NAME"].dropna().unique()),
    default=sorted(platform_filtered_df["GROUP_NAME"].dropna().unique())
)

group_filtered_df = platform_filtered_df[
    platform_filtered_df["GROUP_NAME"].isin(groups)
]


campaigns = st.sidebar.multiselect(
    "Campaign",
    options=sorted(group_filtered_df["CAMPAIGN_NAME"].dropna().unique()),
    default=sorted(group_filtered_df["CAMPAIGN_NAME"].dropna().unique())
)


filtered_df = group_filtered_df[
    group_filtered_df["CAMPAIGN_NAME"].isin(campaigns)
]

total_impressions = filtered_df["IMPRESSIONS"].sum()
total_clicks = filtered_df["CLICKS"].sum()
total_cost = filtered_df["COST"].sum()
total_conversions = filtered_df["CONVERSIONS"].sum()

ctr = (total_clicks / total_impressions * 100) if total_impressions else 0
cpc = (total_cost / total_clicks) if total_clicks else 0


col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Impressions", f"{total_impressions:,}")
col2.metric("Clicks", f"{total_clicks:,}")
col3.metric("Cost", f"${total_cost:,.2f}")
col4.metric("Conversions", f"{total_conversions:,}")
col5.metric("CTR", f"{ctr:.2f}%")
col6.metric("CPC", f"${cpc:.2f}")

st.divider()

st.subheader("Performance Over Time")

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


st.subheader("Campaign Performance")

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


st.subheader("Platform Share")

pie_metric = st.selectbox(
    "Compare platforms by",
    ["COST", "IMPRESSIONS", "CLICKS", "CONVERSIONS"]
)

platform_pie_df = (
    filtered_df
    .groupby("PLATAFORMA", as_index=False)
    .agg({pie_metric: "sum"})
)

if platform_pie_df.empty:
    st.info("Adjust filters to display platform data.")
else:
    pie_chart = (
        alt.Chart(platform_pie_df)
        .mark_arc()
        .encode(
            theta=alt.Theta(field=pie_metric, type="quantitative"),
            color=alt.Color(field="PLATAFORMA", type="nominal"),
            tooltip=["PLATAFORMA", pie_metric]
        )
    )

    st.altair_chart(pie_chart, use_container_width=True)

st.subheader("Performance by Group")

group_metric = st.selectbox(
    "Compare groups by",
    ["COST", "IMPRESSIONS", "CLICKS", "CONVERSIONS"],
    key="group_metric"
)

group_df = (
    filtered_df
    .groupby("GROUP_NAME", as_index=False)
    .agg({group_metric: "sum"})
    .sort_values(group_metric, ascending=False)
)

if group_df.empty:
    st.info("Adjust filters to display group data.")
else:
    bar_chart = (
        alt.Chart(group_df)
        .mark_bar()
        .encode(
            x=alt.X("GROUP_NAME:N", sort="-y", title="Group"),
            y=alt.Y(f"{group_metric}:Q", title=group_metric),
            tooltip=["GROUP_NAME", group_metric]
        )
        .properties(height=400)
    )

    st.altair_chart(bar_chart, use_container_width=True)
