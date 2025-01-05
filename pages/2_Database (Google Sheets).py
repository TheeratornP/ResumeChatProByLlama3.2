import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

####################################################START GETTING DATABASE FOR ANALYSIS########################################################
# Create a connection object
conn = st.connection("gsheets", type=GSheetsConnection)

# Function to read data from Google Sheets and cache it
@st.cache_data
def load_data():
    df = conn.read()
    
    df.columns = [
        "Languages", "Gender", "First Name", "Last Name", "Birth Date", "Email", "Phone", 
        "Desired Job Role", "Work Environment", "Job Type", "Preferred Location", "Near BTS/MRT Line", 
        "Expected Salary", "Years of Experience", "Highest Level of Education", "Skills", "Resume File Name"
    ]
    
    # Convert Birth Date to datetime
    df["Birth Date"] = pd.to_datetime(df["Birth Date"], errors="coerce")
    
    # Ensure the Phone column is treated as a string (to preserve leading zeros)
    df["Phone"] = df["Phone"].astype(str)
    
    # Rename the 'Phone' column to 'Phone (+66)'
    df.rename(columns={"Phone": "Phone (+66)"}, inplace=True)
    
    # Reorder columns as requested
    df = df[[ 
        "First Name", "Last Name", "Gender", "Birth Date", "Email", "Phone (+66)", 
        "Highest Level of Education", "Languages", "Years of Experience", "Skills", 
        "Desired Job Role", "Expected Salary", "Work Environment", "Job Type", 
        "Preferred Location", "Near BTS/MRT Line", "Resume File Name"
    ]]
    
    return df

##################################################END OF GETTING DATABASE FOR ANALYSIS######################################################

# UI for the app
st.title("📊 Google Sheets Data Viewer")
st.markdown("View and download data from Google Sheets with an improved interface.")

# Add a link to the Google Sheets document
st.markdown("[📄 Open Google Sheets](https://docs.google.com/spreadsheets/d/1PY8gZK3C9F4_JTF0wSW_nhjdJAr4wSoQEHHXigib3FY/edit?gid=0#gid=0)")


####################################################REFRESH DATABASE########################################################
# Add a button to refresh data
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()  # Clear the cached data
    st.rerun()  # Rerun the app to reload data

# Load data from Google Sheets
df = load_data()
####################################################END OF REFRESH DATABASE########################################################

# Add a download button for the data
csv_data = df.to_csv(index=False).encode('utf-8')  # `index=False` removes the index from the CSV
st.download_button(
    label="⬇️ Download Data as CSV",
    data=csv_data,
    file_name="google_sheets_data.csv",
    mime="text/csv"
)

# Display the DataFrame without index using st.write
st.markdown("### 📋 Data Table")
st.write(df.style.format(
    {
        "Birth Date": lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else "",
        "Expected Salary": "฿{:,.0f}",
        "Years of Experience": "{:.0f}",
    }
).hide(axis="index"), use_container_width=True)
