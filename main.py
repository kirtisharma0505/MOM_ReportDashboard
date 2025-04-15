import streamlit as st
import pandas as pd
import time
import os

# Path to your CSV file (change this if it's stored elsewhere)
CSV_PATH = "Afina MoM Insights Dashboard - Sheet1.csv"

# Title
st.title("📊 Afina MoM Insights Dashboard")

# Refresh every 10 seconds (optional auto-refresh)
refresh_interval = 10  # seconds
st.caption(f"Refreshing every {refresh_interval} seconds...")

# Auto-refreshing mechanism
def load_data():
    return pd.read_csv(CSV_PATH)

# Initial load
data_load_state = st.text('Loading data...')
df = load_data()
data_load_state.text('')

# Display dataframe
st.dataframe(df)

# Optional: Summary stats
if st.checkbox("Show Summary Stats"):
    st.write(df.describe())

# Optional: Visuals
if st.checkbox("Show Chart"):
    st.line_chart(df.select_dtypes(include='number'))

# Auto-refresh logic
time.sleep(refresh_interval)
st.experimental_rerun()
