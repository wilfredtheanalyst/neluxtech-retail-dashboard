#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 1. Imports & settings
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

sns.set_theme(style="whitegrid")
pd.set_option('display.max_columns', None)
plt.rcParams['figure.figsize'] = (10,6)

# -----------------------------------
# 📂 DATA LOAD
# -----------------------------------

import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache_data
def load_data():
    neluxtech_df = pd.read_csv("NeluxTech Proprietary Retail Dataset.csv")

    # Ensure date column parses properly (handles minor date errors)
    neluxtech_df['date'] = pd.to_datetime(
        neluxtech_df['date'],
        errors='coerce',   # invalid dates become NaT instead of crashing
        dayfirst=True
    )

    return neluxtech_df  # ✅ must be indented exactly 4 spaces under def

# Load the dataset
neluxtech_df = load_data()

# -----------------------------------
# 🧭 DATE FEATURES
# -----------------------------------
neluxtech_df['Year'] = neluxtech_df['date'].dt.year
neluxtech_df['Month'] = neluxtech_df['date'].dt.month
neluxtech_df['Weekday'] = neluxtech_df['date'].dt.day_name()

# -----------------------------------
# 🎛️ SIDEBAR FILTERS
# -----------------------------------
st.sidebar.header("Filter Options")

category = st.sidebar.multiselect("Select Category", sorted(neluxtech_df['category'].unique()), default=neluxtech_df['category'].unique())
ctype = st.sidebar.multiselect("Customer Type", sorted(neluxtech_df['ctype'].unique()), default=neluxtech_df['ctype'].unique())
paym = st.sidebar.multiselect("Payment Method", sorted(neluxtech_df['paym'].unique()), default=neluxtech_df['paym'].unique())
discount = st.sidebar.multiselect("Discount Applied", sorted(neluxtech_df['discapld'].unique()), default=neluxtech_df['discapld'].unique())

filtered_df = neluxtech_df[
    (neluxtech_df['category'].isin(category)) &
    (neluxtech_df['ctype'].isin(ctype)) &
    (neluxtech_df['paym'].isin(paym)) &
    (neluxtech_df['discapld'].isin(discount))
]

st.sidebar.write(f"📦 **{len(filtered_df)} transactions** selected")

# -----------------------------------
# 🔹 KEY METRICS
# -----------------------------------
total_sales = filtered_df['totalsales'].sum()
avg_sales = filtered_df['totalsales'].mean()
total_units = filtered_df['unitsold'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales (KSh)", f"{total_sales:,.0f}")
col2.metric("📈 Avg Sale per Transaction", f"{avg_sales:,.0f}")
col3.metric("🧾 Units Sold", f"{total_units:,.0f}")

# -----------------------------------
# 📅 SALES TREND OVER TIME
# -----------------------------------
sales_trend = filtered_df.groupby('date')['totalsales'].sum().reset_index()
fig_trend = px.line(
    sales_trend,
    x='date',
    y='totalsales',
    markers=True,
    title="📅 Daily Sales Trend",
    color_discrete_sequence=['#2E86DE']
)
fig_trend.update_layout(template="plotly_white")
st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------------
# 📊 SALES BY CATEGORY & CUSTOMER TYPE
# -----------------------------------
fig_bar = px.bar(
    filtered_df,
    x='category',
    y='totalsales',
    color='ctype',
    text_auto=True,
    hover_data=['paym', 'discapld', 'saleslevel'],
    title="🧭 Sales Breakdown by Category & Customer Type",
    color_discrete_sequence=px.colors.qualitative.Vivid
)
fig_bar.update_layout(template="plotly_white", xaxis_title="Category", yaxis_title="Total Sales (KSh)")
st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------------
# 💳 PAYMENT METHOD DISTRIBUTION
# -----------------------------------
paym_sales = filtered_df.groupby('paym')['totalsales'].sum().reset_index()
fig_pie = px.pie(
    paym_sales,
    names='paym',
    values='totalsales',
    hole=0.4,
    title="💳 Payment Method Contribution",
    color_discrete_sequence=px.colors.qualitative.Bold
)
st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------
# 🧍 CUSTOMER GENDER & DISCOUNT EFFECTS
# -----------------------------------
col1, col2 = st.columns(2)

with col1:
    fig_gender = px.bar(
        filtered_df,
        x='cgender',
        y='totalsales',
        color='ctype',
        barmode='group',
        text_auto=True,
        title="👫 Sales by Gender & Customer Type",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_gender.update_layout(template="plotly_white")
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    fig_disc = px.box(
        filtered_df,
        x='discapld',
        y='totalsales',
        color='discapld',
        title="🏷️ Impact of Discounts on Sales",
        color_discrete_sequence=['#00CC96', '#FF6F61']
    )
    fig_disc.update_layout(template="plotly_white")
    st.plotly_chart(fig_disc, use_container_width=True)

# -----------------------------------
# 🗓️ MONTHLY SUMMARY INSIGHTS
# -----------------------------------
st.markdown("### 🧾 Monthly Highlights")

monthly_summary = (
    filtered_df.groupby(['Year', 'Month', 'category'])
    .agg({'totalsales': 'sum'})
    .reset_index()
)

latest_month = int(filtered_df['Month'].max())
latest_year = int(filtered_df['Year'].max())

top_month = monthly_summary[(monthly_summary['Month'] == latest_month) & (monthly_summary['Year'] == latest_year)]
top3_categories = top_month.sort_values('totalsales', ascending=False).head(3)

col1, col2 = st.columns(2)
with col1:
    st.write(f"📆 **Top 3 Categories in {int(latest_month)}/{int(latest_year)}**")
    st.dataframe(top3_categories[['category', 'totalsales']])

with col2:
    paym_month = filtered_df.groupby('paym')['totalsales'].sum().reset_index().sort_values('totalsales', ascending=False)
    fig_month = px.bar(
        paym_month,
        x='paym',
        y='totalsales',
        text_auto=True,
        title=f"💳 Payment Method Performance ({int(latest_month)}/{int(latest_year)})",
        color='paym',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_month.update_layout(template="plotly_white")
    st.plotly_chart(fig_month, use_container_width=True)

# -----------------------------------
# 💾 EXPORT FILTERED DATA
# -----------------------------------
import datetime
import os

st.markdown("### 💾 Export Filtered Data")

# Generate date-stamped filenames (e.g., 2025-10-17)
today_str = datetime.date.today().strftime("%Y-%m-%d")

col1, col2 = st.columns(2)

# ---- CSV EXPORT ----
csv_filename = f"neluxtech_filtered_data_{today_str}.csv"
csv_data = filtered_df.to_csv(index=False).encode('utf-8')

col1.download_button(
    label=f"⬇️ Download CSV ({today_str})",
    data=csv_data,
    file_name=csv_filename,
    mime='text/csv'
)

# ---- EXCEL EXPORT ----
excel_filename = f"neluxtech_filtered_data_{today_str}.xlsx"
excel_path = os.path.join(os.getcwd(), excel_filename)

with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='FilteredData')

with open(excel_path, "rb") as f:
    col2.download_button(
        label=f"📘 Download Excel ({today_str})",
        data=f,
        file_name=excel_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# In[ ]:




