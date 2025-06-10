import streamlit as st
import pandas as pd
import google.generativeai as genai

# 🔐 Configure Gemini API Key
GEMINI_API_KEY = "AIzaSyCL6YH9Oji5IWPNIriG_FejN2IzKZfE1LE"
genai.configure(api_key=GEMINI_API_KEY)

# 🔍 Load Gemini Model
def generate_remark(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

# 📋 Store all remarks
remarks_data = []

st.title("📊 Faculty Task Review & Remark Generator")

# Sidebar Inputs
with st.sidebar:
    faculty_name = st.text_input("Faculty Name")
    department = st.text_input("Department")
    month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    selected_pillars = st.multiselect("Select Pillar(s)", ["CLT", "CFC", "IIPC", "SRI"])

st.write(f"### Faculty: {faculty_name} | Dept: {department} | Month: {month}")

# === CLT ===
if "CLT" in selected_pillars:
    st.subheader("📚 CLT – Center for Learning and Teaching")
    for i in range(1, 6):
        with st.expander(f"Video {i}"):
            video_type = st.selectbox(f"Video Type {i}", ["Lecture", "Case Study", "Design Thinking"], key=f"type_{i}")
            duration = st.number_input(f"Duration in Minutes (Video {i})", min_value=0, key=f"dur_{i}")
            quality = st.selectbox(f"Audio/Video Quality (Video {i})", ["Good", "Poor"], key=f"qual_{i}")
            logo = st.selectbox(f"SNS Logo Present? (Video {i})", ["Yes", "No"], key=f"logo_{i}")
            interactive = "N/A"
            if video_type in ["Case Study", "Design Thinking"]:
                interactive = st.selectbox(f"Interactive with Mentees? (Video {i})", ["Yes", "No"], key=f"int_{i}")
            hashtags = st.selectbox(f"Hashtags Present? (Video {i})", ["Yes", "No"], key=f"hash_{i}")
            desc_len = st.number_input(f"Description Length in Lines (Video {i})", min_value=0, key=f"desc_{i}")

            # 🔍 Generate Prompt
            prompt = f"""
            Faculty uploaded a {video_type} video with the following details:
            Duration: {duration} minutes
            Quality: {quality}
            SNS Logo: {logo}
            Interactive: {interactive}
            Hashtags: {hashtags}
            Description Length: {desc_len} lines
            Evaluate based on: >5 mins, good quality, logo, interactivity (if applicable), hashtags, >2 lines description.
            Provide a professional remark.
            """
            remark = generate_remark(prompt)
            remarks_data.append(["CLT", f"{video_type} Video {i}", remark])
            st.success(remark)

# === CFC ===
if "CFC" in selected_pillars:
    st.subheader("🎨 CFC – Center for Creativity")
    dp = st.selectbox("Design Patent Submitted?", ["Yes", "No"])
    up = st.selectbox("Utility Patent Submitted?", ["Yes", "No"])
    rj1 = st.selectbox("Research Journal 1 Indexed In", ["Scopus", "Web of Science", "None"])
    rj2 = st.selectbox("Research Journal 2 Indexed In", ["Scopus", "Web of Science", "None"])

    prompt = f"Faculty CFC progress: Design Patent: {dp}, Utility Patent: {up}, RJ1: {rj1}, RJ2: {rj2}. Evaluate per target: 1 DP, 1 UP, 2 Indexed Journals."
    remark = generate_remark(prompt)
    remarks_data.append(["CFC", "CFC Progress Summary", remark])
    st.success(remark)

# === IIPC ===
if "IIPC" in selected_pillars:
    st.subheader("🤝 IIPC – Industry-Institute Partnership Cell")
    for a in range(1, 3):
        word_count = st.number_input(f"LinkedIn Article {a} - Word Count", min_value=0, key=f"art_wc_{a}")
        hashtags_ok = st.selectbox(f"Hashtags Present? (Article {a})", ["Yes", "No"], key=f"art_hash_{a}")
        conn_type = st.selectbox(f"Connection {a} Type", ["Alumni", "MNC Expert", "CEO", "Academician", "Startup Founder"], key=f"conn_type_{a}")
        ss = st.selectbox(f"Screenshot Provided? (Connection {a})", ["Yes", "No"], key=f"ss_{a}")
        username = st.text_input(f"Username (Connection {a})", key=f"user_{a}")
        date_conn = st.date_input(f"Connection Date (Connection {a})", key=f"date_{a}")

        prompt = f"IIPC Task: Article {a} with {word_count} words and hashtags present: {hashtags_ok}. Connection with {conn_type}, Screenshot: {ss}, Username: {username}, Date: {date_conn}. Evaluate compliance."
        remark = generate_remark(prompt)
        remarks_data.append(["IIPC", f"Article/Connection {a}", remark])
        st.success(remark)

# === SRI ===
if "SRI" in selected_pillars:
    st.subheader("🌱 SRI – Social Responsibility Initiatives")
    sri_file = st.file_uploader("Upload Parent Connect Excel", type=[".xlsx", ".csv"])
    if sri_file:
        df = pd.read_excel(sri_file) if ".xlsx" in sri_file.name else pd.read_csv(sri_file)
        expected_cols = ["Faculty Name", "Call Date", "Contacted Person's Relationship", "Parent Phone Number", "Mentee Name"]
        missing = [col for col in expected_cols if col not in df.columns]
        if missing:
            st.error(f"Missing Columns: {missing}")
        else:
            prompt = f"SRI Parent Connect data uploaded with {len(df)} rows. Columns verified. Evaluate overall task submission quality."
            remark = generate_remark(prompt)
            remarks_data.append(["SRI", "Parent Connect Task", remark])
            st.success(remark)

# ✅ Final Remarks Table
if remarks_data:
    st.subheader("📄 Final Remarks Table")
    table = pd.DataFrame(remarks_data, columns=["Pillar", "Task", "Remark"])
    st.dataframe(table)
    csv = table.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Remarks as CSV", data=csv, file_name="faculty_remarks.csv", mime="text/csv")
