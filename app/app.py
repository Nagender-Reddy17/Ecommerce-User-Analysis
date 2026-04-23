import streamlit as st
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

st.title("🛒 E-Commerce User Behavior Dashboard")

# ---------------------------
# LOAD DATA (WITH FIXED PATH)
# ---------------------------
@st.cache_data
def load_data():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_path = os.path.join(base_path, "data", "*.csv")
    files = glob.glob(data_path)
    
    df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)
    
    # Cleaning
    df['event_time'] = pd.to_datetime(df['event_time'])
    df['category_code'] = df['category_code'].fillna('unknown')
    df['brand'] = df['brand'].fillna('unknown')
    
    return df

df = load_data()

# ---------------------------
# METRICS
# ---------------------------
col1, col2, col3 = st.columns(3)

total_users = df['user_id'].nunique()
total_events = len(df)
revenue = df[df['event_type']=='purchase']['price'].sum()

col1.metric("👤 Total Users", f"{total_users:,}")
col2.metric("📊 Total Events", f"{total_events:,}")
col3.metric("💰 Total Revenue", f"${revenue:,.2f}")

# ---------------------------
# FUNNEL ANALYSIS
# ---------------------------
st.subheader("📉 Funnel Analysis")

funnel = df['event_type'].value_counts()

views = funnel.get('view', 0)
cart = funnel.get('cart', 0)
purchase = funnel.get('purchase', 0)

col1, col2, col3 = st.columns(3)

col1.metric("View → Cart", f"{(cart/views)*100:.2f}%")
col2.metric("Cart → Purchase", f"{(purchase/cart)*100:.2f}%")
col3.metric("Total Purchases", purchase)

# ---------------------------
# EVENT DISTRIBUTION
# ---------------------------
st.subheader("📊 User Activity Distribution")

st.bar_chart(df['event_type'].value_counts())

# ---------------------------
# TOP PRODUCTS
# ---------------------------
st.subheader("🏆 Top 10 Products")

top_products = df[df['event_type']=='purchase']['product_id'] \
                .value_counts().head(10)

st.bar_chart(top_products)

# ---------------------------
# TOP BRANDS
# ---------------------------
st.subheader("🏷️ Top Brands")

top_brands = df[df['event_type']=='purchase']['brand'] \
                .value_counts().head(10)

st.bar_chart(top_brands)

# ---------------------------
# TIME ANALYSIS
# ---------------------------
st.subheader("⏰ Activity by Hour")

df['hour'] = df['event_time'].dt.hour
hour_counts = df['hour'].value_counts().sort_index()

st.line_chart(hour_counts)

# ---------------------------
# COHORT ANALYSIS
# ---------------------------
st.subheader("📅 Cohort Retention Analysis")

df['month'] = df['event_time'].dt.to_period('M')
df['cohort'] = df.groupby('user_id')['event_time'].transform('min').dt.to_period('M')

cohort_data = df.groupby(['cohort','month'])['user_id'].nunique().reset_index()

cohort_pivot = cohort_data.pivot(index='cohort', columns='month', values='user_id')

# Normalize
retention = cohort_pivot.copy()

for i in range(len(retention)):
    retention.iloc[i] = retention.iloc[i] / retention.iloc[i].dropna().iloc[0]

st.dataframe(retention.round(3))

# ---------------------------
# RAW DATA
# ---------------------------
st.subheader("📄 Raw Data Preview")
st.dataframe(df.head(100))