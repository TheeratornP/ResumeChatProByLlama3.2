import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import random

############################################
# 1) CONNECT TO GOOGLE SHEETS AND LOAD DATA
############################################
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def load_data():
    df = conn.read()
    
    df.columns = [
        "Languages", "Gender", "First Name", "Last Name", "Birth Date", "Email", "Phone", 
        "Desired Job Role", "Work Environment", "Job Type", "Preferred Location", "Near BTS/MRT Line", 
        "Expected Salary", "Years of Experience", "Highest Level of Education", "Skills", "Resume File Name"
    ]
    
    # แปลงคอลัมน์ Languages เป็น string ป้องกัน error split()
    df["Languages"] = df["Languages"].fillna("").astype(str)

    # Convert Birth Date to datetime
    df["Birth Date"] = pd.to_datetime(df["Birth Date"], errors="coerce")
    
    # Phone -> Phone (+66)
    df["Phone"] = df["Phone"].astype(str)
    df.rename(columns={"Phone": "Phone (+66)"}, inplace=True)
    
    # Reorder columns
    df = df[[ 
        "First Name", "Last Name", "Gender", "Birth Date", "Email", "Phone (+66)", 
        "Highest Level of Education", "Languages", "Years of Experience", "Skills", 
        "Desired Job Role", "Expected Salary", "Work Environment", "Job Type", 
        "Preferred Location", "Near BTS/MRT Line", "Resume File Name"
    ]]
    return df

############################################
# 2) LAT/LONG MAPPING & JITTER
############################################
location_coordinates = {
    "Bangkok": (13.7563, 100.5018),
    "Chiang Mai": (18.7883, 98.9853),
    "Khon Kaen": (16.4322, 102.8236),
    "Phuket": (7.8804, 98.3923),
    "Chiang Rai": (19.9105, 99.8406),
    "Chonburi": (13.3611, 100.9847),
    "Saraburi": (14.5302, 100.9103),
    "Samutprakan": (13.5991, 100.5967),
    "Other": (13.7367, 100.5231),  # Default to Bangkok
}

def add_coordinates_with_jitter(data):
    def jitter(value, delta=0.01):
        return value + random.uniform(-delta, delta)

    data["Latitude"] = data["Preferred Location"].map(
        lambda loc: jitter(location_coordinates.get(loc, (13.7367, 100.5231))[0])
    )
    data["Longitude"] = data["Preferred Location"].map(
        lambda loc: jitter(location_coordinates.get(loc, (13.7367, 100.5231))[1])
    )
    return data

############################################
# 3) MAIN APP
############################################
def main():
    st.title(":office: Job Role Analysis Dashboard with Advanced Filtering")
    st.subheader("Select Job Roles")
    
    # โหลดข้อมูลสำหรับ multiselect
    data = load_data()
    job_roles = data["Desired Job Role"].unique()

    selected_job_roles = st.multiselect(
        "Select Job Roles Desired",
        options=list(job_roles),
        default=list(job_roles),
    )
    # ------------------------------------------------------------------------

    # ข้อความอธิบายอื่น ๆ
    st.write("Explore job roles, applicant demographics, expected salaries, and experience levels.")

    # ลองคืนค่า data ให้ filtering ใช้ต่อ
    # (ถ้าเลือก Job Roles ใด ๆ กรอง data ทันที)
    if selected_job_roles:
        filtered_data = data[data["Desired Job Role"].isin(selected_job_roles)]
    else:
        filtered_data = data

    # เพิ่ม jitter lat/long และ Full Name
    filtered_data = add_coordinates_with_jitter(filtered_data)
    filtered_data["Full Name"] = filtered_data["First Name"] + " " + filtered_data["Last Name"]
   

    ##################################################
    # Section 1: Gender Distribution
    ##################################################
    st.subheader("👥 Gender Distribution")
    gender_images = {
        "Male": "https://cdn-icons-png.flaticon.com/512/236/236831.png",
        "Female": "https://cdn-icons-png.flaticon.com/512/6833/6833591.png",
        "Other": "https://cdn-icons-png.flaticon.com/512/2620/2620829.png",
    }

    gender_order = ["Male", "Female", "Other"]
    gender_counts = (
        filtered_data["Gender"]
        .value_counts()
        .reindex(gender_order)
        .reset_index()
    )
    gender_counts.columns = ["Gender", "Count"]

    cols = st.columns(len(gender_counts))
    for i, row in gender_counts.iterrows():
        with cols[i]:
            st.image(
                gender_images.get(row["Gender"], gender_images["Other"]), width=100
            )
            st.markdown(f"**{row['Gender']}**")
            st.markdown(f"**{row['Count']} Applicants**")

    ##################################################
    # Section 2: Tree Map for Job Roles
    ##################################################
    st.subheader("🗂️ Job Role Tree Map")
    job_role_summary = (
        filtered_data.groupby("Desired Job Role")
        .agg({"Expected Salary": "mean", "Desired Job Role": "count"})
        .rename(
            columns={
                "Expected Salary": "Average Salary",
                "Desired Job Role": "Number of Applicants",
            }
        )
        .reset_index()
    )
    fig_tree = px.treemap(
        job_role_summary,
        path=["Desired Job Role"],
        values="Number of Applicants",
        hover_data={
            "Desired Job Role": True,
            "Number of Applicants": True,
            "Average Salary": ":,.0f",
        },
        color="Number of Applicants",
        color_continuous_scale="Blues",
        title="Job Roles by Number of Applicants and Average Salary",
    )
    fig_tree.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        title_font=dict(size=24, color="lightblue"),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, color="white"),
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    ##################################################
    # Section 3: Bar Chart for Expected Salary (Top 10)
    ##################################################
    st.subheader("💰 Top 10 Expected Salaries")
    top_salary_data = (
        filtered_data.sort_values(by="Expected Salary", ascending=False).head(10)
    )
    fig_salary = px.bar(
        top_salary_data,
        x="Full Name",
        y="Expected Salary",
        title="💰 Top 10 Expected Salaries",
        labels={"Expected Salary": "Salary (THB)", "Full Name": "Applicant"},
    )
    fig_salary.update_traces(
        textposition="outside",
        texttemplate='%{y:,.0f}',
        cliponaxis=False
    )
    fig_salary.update_layout(
        xaxis_tickangle=-45,
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(tickformat=",")
    )
    st.plotly_chart(fig_salary, use_container_width=True)

    ##################################################
    # Section 4: Horizontal Bar Chart (Experience, Top 10)
    ##################################################
    st.subheader("⏳ Top 10 Applicants by Years of Experience")
    top_experience_data = (
        filtered_data.sort_values(by="Years of Experience", ascending=False).head(10)
    )
    fig_experience = px.bar(
        top_experience_data,
        x="Years of Experience",
        y="Full Name",
        orientation="h",
        text="Years of Experience",
        title="⏳ Top 10 Applicants by Years of Experience",
        labels={
            "Years of Experience": "Experience (Years)", 
            "Full Name": "Applicant"
        },
    )
    fig_experience.update_traces(
        textposition="outside",
        marker_color="lightgreen"
    )
    fig_experience.update_layout(
        xaxis_tickangle=0,
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_experience, use_container_width=True)

    ##################################################
    # Section 5: Map Visualization
    ##################################################
    st.subheader("🗺️ Map of Applicant Locations")
    fig_map = px.scatter_mapbox(
        filtered_data,
        lat="Latitude",
        lon="Longitude",
        hover_name="Full Name",
        hover_data={"Preferred Location": True, "Desired Job Role": True},
        color_discrete_sequence=["blue"],
        zoom=5,
        height=500,
        title="🗺️ Applicant Locations by Preferred Location",
    )
    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    ##################################################
    # ADVANCED FILTERING SECTION
    ##################################################
    st.subheader("🔍 Advanced Filters for Applicants")
    with st.form("filter_form"):
        min_salary = st.number_input("Minimum Expected Salary (THB)", min_value=0, value=0)
        max_salary = st.number_input("Maximum Expected Salary (THB)", min_value=0, value=1000000)
        min_experience = st.number_input("Minimum Years of Experience", min_value=0, value=0)

        education_options = data["Highest Level of Education"].unique()
        selected_education = st.multiselect(
            "Select Education Levels",
            options=education_options,
            default=education_options,
        )

        # Languages
        all_languages = set()
        for langs in data["Languages"]:
            lang_list = [x.strip() for x in langs.split(",")]
            for lang in lang_list:
                all_languages.add(lang)
        unique_languages = sorted(list(all_languages))
        selected_languages = st.multiselect(
            "Select Languages",
            options=unique_languages,
            default=unique_languages,
        )

        environment_options = data["Work Environment"].unique()
        selected_environments = st.multiselect(
            "Select Work Environments",
            options=environment_options,
            default=environment_options,
        )

        job_type_options = data["Job Type"].unique()
        selected_job_types = st.multiselect(
            "Select Job Types",
            options=job_type_options,
            default=job_type_options,
        )

        location_options = data["Preferred Location"].unique()
        selected_locations = st.multiselect(
            "Select Preferred Locations",
            options=location_options,
            default=location_options,
        )

        bts_options = [True, False]
        selected_bts = st.multiselect(
            "Near BTS/MRT Line",
            options=bts_options,
            default=bts_options
        )

        submit_button = st.form_submit_button("Apply Filters")

    if submit_button:
        def has_selected_language(langs_str, selected_set):
            lang_list = [x.strip() for x in langs_str.split(",")]
            return len(set(lang_list).intersection(selected_set)) > 0

        lang_set = set(selected_languages)

        advanced_filtered_data = filtered_data[
            (filtered_data["Expected Salary"] >= min_salary)
            & (filtered_data["Expected Salary"] <= max_salary)
            & (filtered_data["Years of Experience"] >= min_experience)
            & (filtered_data["Highest Level of Education"].isin(selected_education))
            & (filtered_data["Languages"].apply(lambda x: has_selected_language(x, lang_set)))
            & (filtered_data["Work Environment"].isin(selected_environments))
            & (filtered_data["Job Type"].isin(selected_job_types))
            & (filtered_data["Preferred Location"].isin(selected_locations))
            & (filtered_data["Near BTS/MRT Line"].isin(selected_bts))
        ]

        st.subheader("📋 Filtered Applicants")
        st.write(f"Total Applicants Found: {len(advanced_filtered_data)}")
        st.dataframe(advanced_filtered_data)

if __name__ == "__main__":
    main()





































