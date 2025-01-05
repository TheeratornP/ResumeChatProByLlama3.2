import streamlit as st
import pandas as pd

# List of predefined locations
locations_list = [
    "Bang Kapi", "Bang Rak", "Chatuchak", "Huai Khwang", "Khlong Toei", 
    "Phra Nakhon", "Ratchathewi", "Sathon", "Watthana"
]

# Sample mock data for job posts with some positions having negotiable salaries
job_data = [
    {
        "Position": "Software Engineer",
        "Salary Range (THB)": "30,000 - 50,000",
        "Experience Needed (Years)": "2 - 3",
        "Job Level": "Junior",
        "Location": "Bang Kapi"
    },
    {
        "Position": "Data Scientist",
        "Salary Range (THB)": "Negotiable",
        "Experience Needed (Years)": "3 - 7",
        "Job Level": "Senior",
        "Location": "Chatuchak"
    },
    {
        "Position": "Project Manager",
        "Salary Range (THB)": "60,000 - 100,000",
        "Experience Needed (Years)": "5 - 10",
        "Job Level": "Manager",
        "Location": "Ratchathewi"
    },
    {
        "Position": "Marketing Specialist",
        "Salary Range (THB)": "Negotiable",
        "Experience Needed (Years)": "0 - 1",
        "Job Level": "Junior",
        "Location": "Sathon"
    },
    {
        "Position": "UX/UI Designer",
        "Salary Range (THB)": "35,000 - 60,000",
        "Experience Needed (Years)": "2 - 3",
        "Job Level": "Mid",
        "Location": "Huai Khwang"
    },
    {
        "Position": "System Architect",
        "Salary Range (THB)": "70,000 - 120,000",
        "Experience Needed (Years)": 6,
        "Job Level": "Senior",
        "Location": "Watthana"
    },
    {
        "Position": "Business Analyst",
        "Salary Range (THB)": "Negotiable",
        "Experience Needed (Years)": "4 - 6",
        "Job Level": "Mid",
        "Location": "Phra Nakhon"
    },
    {
        "Position": "HR Manager",
        "Salary Range (THB)": "Negotiable",
        "Experience Needed (Years)": 7,
        "Job Level": "Manager",
        "Location": "Khlong Toei"
    }
]

# Convert mock data to DataFrame
df_jobs = pd.DataFrame(job_data)

# Streamlit UI
st.title("📢 Job Postings")

# Description
st.markdown("""
Welcome to the **Job Postings** page. Below are the job positions currently available.
""")

# Display job posts as cards
st.markdown("### Available Job Positions")

# Loop through the data and display each job as a card
for _, row in df_jobs.iterrows():
    with st.container():
        # Use columns to create a nice layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{row['Position']}**")
            if row["Salary Range (THB)"] == "Negotiable":
                st.markdown("**Salary:** Negotiable")
            else:
                st.markdown(f"**Salary Range:** {row['Salary Range (THB)']}")
            st.markdown(f"**Experience Needed:** {row['Experience Needed (Years)']} years")
            st.markdown(f"**Location:** {row['Location']}")
            
            # Add the "Apply this position" button
            if st.button("Apply this position", key=row['Position']):
                st.write(f"🔗 Application link for **{row['Position']}** goes here.")
        
        with col2:
            # Add job level as colored badge with black font color
            if row['Job Level'] == 'Junior':
                color = 'lightblue'
            elif row['Job Level'] == 'Senior':
                color = 'lightgreen'
            elif row['Job Level'] == 'Manager':
                color = 'lightcoral'
            else:
                color = 'lightgray'
            
            st.markdown(f'<div style="background-color:{color}; padding: 5px; border-radius: 5px; text-align: center; color: black;">{row["Job Level"]}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
