import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIG ===
SHEET_ID = "1i39YgZHPuMVpXh_raQt-fdXwqLVVHkfdCaC8ZzyU4U0"
SHEET_NAME = "Sheet1"  # Replace with your sheet name
CREDENTIALS_FILE = "credentials.json"  # You need to create this
st.set_page_config("📈 Afina MoM Sales Dashboard", layout="wide")

# === LOAD DATA ===
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    try:
        # Set up credentials
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet and sheet
        try:
            spreadsheet = client.open_by_key(SHEET_ID)
        except Exception as e:
            st.error(f"Error opening spreadsheet: {e}")
            return pd.DataFrame()
            
        try:
            worksheet = spreadsheet.worksheet(SHEET_NAME)
        except Exception as e:
            st.error(f"Error opening worksheet {SHEET_NAME}: {e}")
            return pd.DataFrame()
        
        # Get all values and convert to DataFrame
        try:
            data = worksheet.get_all_values()
        except Exception as e:
            st.error(f"Error getting values: {e}")
            return pd.DataFrame()
            
        # Create DataFrame - skip title row and use row 2 (index 1) as headers
        # Based on the screenshot, headers are in row 2 of the spreadsheet
        if len(data) > 2:
            headers = data[1]  # Use row 2 (index 1) as headers
            values = data[2:]  # Use data starting from row 3 (index 2)
            df = pd.DataFrame(values, columns=headers)
        else:
            st.error("Not enough rows in the data")
            return pd.DataFrame()
        
        # Clean and convert numeric columns using a safer approach
        numeric_columns = [
            'Website Net Sales', 'Δ Website', 'Amazon Net Sales', 'Δ Amazon', 
            'MoM % Website', 'MoM % Amazon'
        ]
        
        for col in numeric_columns:
            if col not in df.columns:
                st.error(f"Column '{col}' not found in data")
                continue
                
            # Make a copy to avoid SettingWithCopyWarning
            df = df.copy()
            
            # For percentage columns
            if 'MoM %' in col:
                # Remove % signs and convert to float
                df[col] = df[col].apply(lambda x: str(x).replace('%', '').strip())
                df[col] = df[col].apply(lambda x: '0' if x == '-' or x == '' else x)
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                # For money columns, remove $, commas
                df[col] = df[col].apply(lambda x: str(x).replace('$', '').replace(',', '').strip())
                df[col] = df[col].apply(lambda x: '0' if x == '-' or x == '' else x)
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("Failed to load data. Please check your credentials and sheet setup.")
    st.stop()

latest = df.iloc[-1]

# === HEADLINE KPIs ===
st.title("📊 Afina MoM Sales Performance Dashboard")

if not df.empty and all(col in df.columns for col in ['Month', 'Website Net Sales', 'Amazon Net Sales', 'MoM % Website', 'MoM % Amazon']):
    latest = df.iloc[-1]
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    # Safely get values with fallbacks
    web_sales = latest.get('Website Net Sales', 0)
    web_sales = float(web_sales) if pd.notna(web_sales) else 0
    
    amz_sales = latest.get('Amazon Net Sales', 0)
    amz_sales = float(amz_sales) if pd.notna(amz_sales) else 0
    
    web_mom = latest.get('MoM % Website', 0)
    web_mom = float(web_mom) if pd.notna(web_mom) else 0
    
    amz_mom = latest.get('MoM % Amazon', 0)
    amz_mom = float(amz_mom) if pd.notna(amz_mom) else 0
    
    # Display metrics with proper formatting
    kpi1.metric("Website Sales", f"${web_sales:,.0f}", f"{web_mom:.2f}%")
    kpi2.metric("Amazon Sales", f"${amz_sales:,.0f}", f"{amz_mom:.2f}%")
    kpi3.metric("Total Sales", f"${web_sales + amz_sales:,.0f}")
    
    # MoM change highlight
    change_type = "increase" if (web_mom > 0 or amz_mom > 0) else "decrease"
    highlight_text = f"✅ Website changed by {web_mom:+.2f}%, Amazon changed by {amz_mom:+.2f}%"
    kpi4.success(highlight_text if change_type == "increase" else highlight_text.replace("✅", "⚠️"))
    
    # Continue with the rest of the dashboard only if we have data
    
    # === LINE CHART: Net Sales Trend ===
    st.subheader("📈 Net Sales Over Time")
    if 'Month' in df.columns and 'Website Net Sales' in df.columns and 'Amazon Net Sales' in df.columns:
        line_df = df.set_index("Month")[["Website Net Sales", "Amazon Net Sales"]]
        st.plotly_chart(px.line(line_df, markers=True, labels={"value": "Sales ($)", "Month": "Month"}, title="Website vs Amazon Net Sales"))
    else:
        st.error("Missing required columns for sales trend chart")
    
    # === LINE CHART: MoM % Change Trend ===
    st.subheader("📈 MoM % Growth Trend Over Time")
    if 'Month' in df.columns and 'MoM % Website' in df.columns and 'MoM % Amazon' in df.columns:
        mom_line = df.set_index("Month")[["MoM % Website", "MoM % Amazon"]]
        st.plotly_chart(px.line(mom_line, markers=True, labels={"value": "MoM %", "Month": "Month"}, title="MoM % Website vs Amazon"))
    else:
        st.error("Missing required columns for MoM % trend chart")
    
    # === BAR CHART: Δ Sales (Delta) ===
    st.subheader("📊 MoM Δ (Delta) in Sales")
    if 'Month' in df.columns and 'Δ Website' in df.columns and 'Δ Amazon' in df.columns:
        bar_delta = df[["Month", "Δ Website", "Δ Amazon"]].copy().melt(id_vars="Month", var_name="Channel", value_name="Delta")
        st.plotly_chart(px.bar(bar_delta, x="Month", y="Delta", color="Channel", barmode="group", 
                          color_discrete_map={"Δ Website": "#1f77b4", "Δ Amazon": "#ff7f0e"},
                          title="Month-over-Month Δ in Sales"))
    else:
        st.error("Missing required columns for delta bar chart")
else:
    st.error("Required columns are missing from the data. Please check your spreadsheet format.")
    st.stop()

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
# with st.expander("🔎 Filter Options"):
#     selected_months = st.multiselect("Select Months", options=df['Month'].unique(), default=list(df['Month'].unique()))
#     filtered = df[df['Month'].isin(selected_months)]
#     st.dataframe(filtered)

# === FOOTER ===
st.caption("Data updates automatically from Google Sheets. Last updated view: most recent 4 months")

# Add refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
    
# === AUTO REFRESH ===
def start_auto_refresh():
    st.cache_data.clear()
    time.sleep(300)  # Refresh every 5 minutes
    st.rerun()

if __name__ == '__main__':
    # Remove old file watcher code that won't work with Google Sheets
    pass