import streamlit as st
import pandas as pd
import re
import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

# Define the scope for Google Sheets API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Path to your service account JSON file (relative path)
creds_path = os.path.join(os.getcwd(), 'tacocat-446810-aef4d2e029b8.json')  # Adjust if needed

# Authenticate using the service account JSON file
creds = Credentials.from_service_account_file(creds_path, scopes=scope)

# Authenticate and create a client to interact with Google Sheets
client = gspread.authorize(creds)

# Open the spreadsheet using the URL
spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1PY8gZK3C9F4_JTF0wSW_nhjdJAr4wSoQEHHXigib3FY/edit?gid=0')

# Select the first sheet
sheet = spreadsheet.sheet1

# Initialize session state
def initialize_state():
    if 'submissions' not in st.session_state:
        try:
            st.session_state.submissions = pd.DataFrame(columns=[ 
                "Languages", "Gender", "First Name", "Last Name", "Birth Date", "Email", "Phone", 
                "Desired Job Role", "Work Environment", "Job Type", "Preferred Location", "Near BTS/MRT Line", 
                "Expected Salary", "Years of Experience", "Highest Level of Education", "Skills", "Resume File Name"
            ])
        except Exception as e:
            st.error(f"Error initializing session state: {e}")

# Validate email format
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Display job seeker form
def display_form():
    st.markdown("## 🎯 **Job Seeker Application Form**")
    st.markdown("Please fill out the form below to apply for your desired job role. Fields marked with * are required.")

    with st.form("job_seeker_form"):
        # Personal details
        st.markdown("### 👤 **Personal Details**")
        gender = st.radio("Gender*", ["Male", "Female", "Other"], key="gender")
        
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name*", key="first_name")
        with col2:
            last_name = st.text_input("Last Name*", key="last_name")
        
        birth_date = st.date_input("Birth Date*", key="birth_date", help="Select your date of birth",
                                   value=datetime.date(2002, 1, 1), min_value=datetime.date(1965, 1, 1), max_value=datetime.date(2007, 12, 31))
        
        # Email and Phone on the same line
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email Address*", key="email", help="e.g., example@domain.com")
        with col2:
            phone = st.text_input("Phone Number*", key="phone", help="Enter a valid phone number")
        
        # Preferred Languages (checkboxes)
        st.markdown("### 🌍 **Preferred Languages**")
        languages_options = ["Thai", "English", "Japanese", "Chinese", "Other"]
        languages_selected = [option for option in languages_options if st.checkbox(option, key=f"lang_{option}")]

        # Job-related details
        st.divider()
        st.markdown("### 💼 **Job Preferences**")
        
        # Desired Job Role on the first column
        job_roles = [
            "",  # Blank option
            "Software Development", "Data Science", "Product Management", "Design", 
            "Marketing", "Sales", "Human Resources", "Customer Support", 
            "Finance", "Project Management", "Content Creation", "UI/UX Design", 
            "Business Analysis", "Engineering", "Cybersecurity", "Operations", 
            "Production", "Other"
        ]
        job_role = st.selectbox("Desired Job Role*", job_roles, key="job_role")
        
        # Work Environment (checkboxes)
        st.markdown("### 🏢 **Work Environment**")
        work_environment_options = ["Full Remote", "Hybrid", "On-site"]
        work_environment_selected = [option for option in work_environment_options if st.checkbox(option, key=f"work_env_{option}")]

        # Job Type (checkboxes)
        st.markdown("### 💼 **Job Type**")
        job_type_options = ["Full-time", "Contract", "Internship", "Freelance"]
        job_type_selected = [option for option in job_type_options if st.checkbox(option, key=f"job_type_{option}")]
        
        # Salary
        expected_salary = st.number_input("Expected Salary (THB)*", min_value=0, step=1000, key="salary")
        
        # Years of Experience and Highest Level of Education on the same line
        col1, col2 = st.columns(2)
        with col1:
            years_of_experience = st.number_input("Years of Experience*", min_value=0, max_value=50, step=1, key="experience")
        with col2:
            education = st.selectbox("Highest Level of Education*", ["", "High School", "Associate Degree", "Bachelor's Degree", "Master's Degree", "PhD"], key="education")
        
        # Preferred Location (checkboxes in 5 rows, 2 columns)
        st.divider()
        st.markdown("### 🌍 **Preferred Location**")
        locations = [
            "Bang Kapi", "Bang Rak", "Chatuchak", "Huai Khwang", "Khlong Toei", 
            "Phra Nakhon", "Ratchathewi", "Sathon", "Watthana", "Others"
        ]
        cols = st.columns(2)
        location_selected = []
        for i, location in enumerate(locations):
            with cols[i % 2]:
                if st.checkbox(location, key=f"location_{location}"):
                    location_selected.append(location)

        # Checkbox for Near BTS/MRT Line
        st.markdown("### 🚉 **Near BTS/MRT Line**")  # Added header for this section
        near_bts_mrt = st.checkbox("Near BTS/MRT Line", key="near_bts_mrt")
        
        # Upload Resume
        st.divider()
        st.markdown("### 📄 **Upload Resume**")
        resume = st.file_uploader("Upload your resume (PDF only)*", type=["pdf"], key="resume")

        # Check if resume is uploaded
        if resume is None:
            st.warning("You need to upload your resume to submit the application.")

        # Additional details
        st.divider()
        st.markdown("### 🛠️ **Additional Details**")
        skills = st.text_area("Skills", help="e.g., Python, JavaScript, SQL", key="skills")
        
        submit_button = st.form_submit_button("Submit Application")
        
        # Validation before submission
        if submit_button:
            # Validate that all required fields are filled
            if not first_name or not last_name or not email or not phone or not job_role or not expected_salary or not years_of_experience or not education or not resume:
                st.error("Please fill out all required fields before submitting.")
            elif not validate_email(email):
                st.error("Invalid email address. Please enter a valid email.")
            else:
                # Save the submission to the Google Sheet
                save_submission_to_sheet(languages_selected, gender, first_name, last_name, birth_date, email, phone, job_role, 
                                          work_environment_selected, job_type_selected, location_selected, near_bts_mrt, 
                                          expected_salary, years_of_experience, education, skills, resume.name)
                
                # Save the uploaded resume to a folder
                save_folder = os.path.join("uploaded_resumes", job_role)
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)
                
                resume_filename = f"{first_name}_{last_name}_resume.pdf"
                with open(os.path.join(save_folder, resume_filename), "wb") as f:
                    f.write(resume.getbuffer())
                st.success("Application Submitted Successfully!")

# Save submission to Google Sheet
def save_submission_to_sheet(languages, gender, first_name, last_name, birth_date, email, phone, job_role, work_environment, 
                              job_type, preferred_location, near_bts_mrt, salary, experience, education, skills, resume_file):
    try:
        # Ensure phone number is treated as a string
        phone = str(phone).strip()  # This ensures the phone number is a string without extra spaces
        
        # Add quotes around the phone number to ensure it's treated as a string in Google Sheets
        phone = f'{phone}'

        new_data = [
            ", ".join(languages),  # Save the selected languages as a comma-separated string
            gender,
            first_name,
            last_name,
            str(birth_date),
            email,
            phone,  # Phone number is now a string with quotes
            job_role,
            ", ".join(work_environment),  # Save as comma-separated string
            ", ".join(job_type),  # Save as comma-separated string
            ", ".join(preferred_location),  # Save selected locations as comma-separated string
            near_bts_mrt, 
            salary,
            experience,
            education,
            skills,
            resume_file
        ]
        sheet.append_row(new_data)
    except Exception as e:
        st.error(f"Error saving submission to Google Sheets: {e}")

# Initialize state and form display
initialize_state()
display_form()
