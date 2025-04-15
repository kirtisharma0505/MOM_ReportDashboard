import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# === CONFIG ===
CSV_PATH = "csv_mom/Afina MoM Insights Dashboard - Sheet1.csv"
st.set_page_config("📈 Afina MoM Sales Dashboard", layout="wide")

# === LOAD DATA ===
@st.cache_data(ttl=10)
def load_data():
    df = pd.read_csv(CSV_PATH, skiprows=1)
    df.columns = df.columns.str.strip()
    
    # Convert sales columns
    for col in ['Website Net Sales', 'Δ Website', 'Amazon Net Sales', 'Δ Amazon']:
        df[col] = df[col].replace('[\$,]', '', regex=True).replace('-', '0')
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert MoM % columns
    for col in ['MoM % Website', 'MoM % Amazon']:
        df[col] = df[col].replace('%', '', regex=True).replace('-', '0')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

df = load_data()
latest = df.iloc[-1]

# === HEADLINE KPIs ===
st.title("📊 Afina MoM Sales Performance Dashboard")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Website Sales", f"${latest['Website Net Sales']:,.0f}", f"{latest['MoM % Website']:.2f}%")
kpi2.metric("Amazon Sales", f"${latest['Amazon Net Sales']:,.0f}", f"{latest['MoM % Amazon']:.2f}%")
kpi3.metric("Total Sales", f"${latest['Website Net Sales'] + latest['Amazon Net Sales']:,.0f}")

# MoM change highlight
web_mom = latest['MoM % Website']
amz_mom = latest['MoM % Amazon']
change_type = "increase" if (web_mom > 0 or amz_mom > 0) else "decrease"
highlight_text = f"✅ Website rebounded in {latest['Month']} with {web_mom:+.2f}%, Amazon changed by {amz_mom:+.2f}%"
kpi4.success(highlight_text if change_type == "increase" else highlight_text.replace("✅", "⚠️"))

# === LINE CHART: Net Sales Trend ===
st.subheader("📈 Net Sales Over Time")
line_df = df.set_index("Month")[["Website Net Sales", "Amazon Net Sales"]]
st.plotly_chart(px.line(line_df, markers=True, labels={"value": "Sales ($)", "Month": "Month"}, title="Website vs Amazon Net Sales"))

# === LINE CHART: MoM % Change Trend (Fix) ===
st.subheader("📈 MoM % Growth Trend Over Time")
mom_line = df.set_index("Month")[["MoM % Website", "MoM % Amazon"]]
st.plotly_chart(px.line(mom_line, markers=True, labels={"value": "MoM %", "Month": "Month"}, title="MoM % Website vs Amazon"))

# === BAR CHART: Δ Sales (Delta) ===
st.subheader("📊 MoM Δ (Delta) in Sales")
bar_delta = df[["Month", "Δ Website", "Δ Amazon"]].copy().melt(id_vars="Month", var_name="Channel", value_name="Delta")
st.plotly_chart(px.bar(bar_delta, x="Month", y="Delta", color="Channel", barmode="group", 
                      color_discrete_map={"Δ Website": "#1f77b4", "Δ Amazon": "#ff7f0e"},
                      title="Month-over-Month Δ in Sales"))

# === BAR CHART: MoM % Change ===
st.subheader("📉 MoM % Change (Bar View)")
mom_pct = df[["Month", "MoM % Website", "MoM % Amazon"]].copy().melt(id_vars="Month", var_name="Channel", value_name="MoM %")
st.plotly_chart(px.bar(mom_pct, x="Month", y="MoM %", color="Channel", barmode="group", 
                      color_discrete_map={"MoM % Website": "#2ca02c", "MoM % Amazon": "#d62728"},
                      title="MoM % Growth/Decline"))

# === PIE CHART: Share of Sales ===
st.subheader("📌 Share of Website vs Amazon Sales (Latest Month)")
latest_sales = {
    "Website": latest["Website Net Sales"],
    "Amazon": latest["Amazon Net Sales"]
}
st.plotly_chart(px.pie(names=latest_sales.keys(), values=latest_sales.values(), hole=0.5, title=f"Sales Share - {latest['Month']}"))

# === INSIGHTS SECTION ===
st.subheader("💡 Key Insights")

max_web = df[df['MoM % Website'] == df['MoM % Website'].max()].iloc[0]
max_amz = df[df['MoM % Amazon'] == df['MoM % Amazon'].max()].iloc[0]

st.markdown(f"✅ Amazon spiked in **{max_amz['Month']}** with **{max_amz['MoM % Amazon']:.2f}%** growth.")
st.markdown(f"✅ Website rebounded in **{max_web['Month']}** with **{max_web['MoM % Website']:.2f}%** growth.")

# === OPTIONAL FILTER ===
with st.expander("🔎 Filter Options"):
    selected_months = st.multiselect("Select Months", options=df['Month'].unique(), default=list(df['Month'].unique()))
    filtered = df[df['Month'].isin(selected_months)]
    st.dataframe(filtered)

# === FOOTER ===
st.caption("Data updates automatically from CSV. Last updated view: most recent 4 months")
