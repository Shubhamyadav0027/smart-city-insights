import sqlite3
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import folium
from streamlit_folium import st_folium
st.set_page_config(
    page_title="Smart City Insight",
    page_icon="🏙️",
    layout="wide"
)

# STEP 17A: BASIC LOGIN SYSTEM

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏙️ Smart City Insights")
    st.subheader("🔐 Admin Login")

    with st.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

    if login_button:
        if username == "admin" and password == "CityPulse@123":
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.stop()


# PROFESSIONAL CITYPULSE AI THEME
st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
        color: #1E293B;
    }

    /* Fix invisible headings and text */
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp p,
    .stApp label,
    .stApp li,
    div[data-testid="stMarkdownContainer"] {
        color: #1E293B !important;
        opacity: 1 !important;
    }

    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: #1E293B !important;
    }

    [data-testid="stSidebar"] {
        background-color: #14213D;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF;
    }
    /* Make sidebar navigation text visible */
[data-testid="stSidebar"] [role="radiogroup"] label,
[data-testid="stSidebar"] [role="radiogroup"] label p,
[data-testid="stSidebar"] [role="radiogroup"] label div,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #FFFFFF !important;
    opacity: 1 !important;
    visibility: visible !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] button p {
    color: #FFFFFF !important;
    opacity: 1 !important;
}
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #14213D !important;
        font-weight: 700;
    }

    h1, h2, h3 {
        color: #14213D !important;
    }

    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 8px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# STEP 9: SQLITE DATABASE
# -------------------------------
DB_NAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "citypulse.db"
)


def init_database():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            Complaint_ID TEXT PRIMARY KEY,
            Date TEXT,
            Ward TEXT,
            Problem TEXT,
            Status TEXT,
            Severity TEXT
        )
    """)

    conn.commit()
    conn.close()



def load_complaints():
    conn = sqlite3.connect(DB_NAME)

    data = pd.read_sql_query(
        "SELECT * FROM complaints",
        conn
    )

    conn.close()
    return data


def save_complaints(data):
    conn = sqlite3.connect(DB_NAME)

    rows = data[
        [
            "Complaint_ID",
            "Date",
            "Ward",
            "Problem",
            "Status",
            "Severity"
        ]
    ].copy()

    rows["Date"] = pd.to_datetime(
        rows["Date"]
    ).dt.strftime("%Y-%m-%d")

    conn.executemany("""
        INSERT OR REPLACE INTO complaints
        (Complaint_ID, Date, Ward, Problem, Status, Severity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, rows.itertuples(index=False, name=None))

    conn.commit()
    conn.close()


init_database()

# -------------------------------
# 1. DEMO DATASET
# -------------------------------
@st.cache_data
def create_demo_data():
    import random

    random.seed(42)

    wards = [
        "Ward 1", "Ward 2", "Ward 3", "Ward 4",
        "Ward 5", "Ward 6", "Ward 7", "Ward 8"
    ]

    problems = [
        "Garbage", "Water Supply", "Traffic",
        "Pollution", "Street Light"
    ]

    rows = []
    today = date.today()

    for i in range(350):
        ward = random.choice(wards)

        problem = random.choices(
            problems,
            weights=[30, 25, 20, 15, 10]
        )[0]

        status = random.choices(
            ["Resolved", "Pending", "In Progress"],
            weights=[55, 25, 20]
        )[0]

        complaint_date = today - timedelta(
            days=random.randint(0, 89)
        )

        rows.append({
            "Complaint_ID": f"CP{i + 1:04d}",
            "Date": complaint_date,
            "Ward": ward,
            "Problem": problem,
            "Status": status,
            "Severity": random.choice(
                ["Low", "Medium", "High"]
            )
        })

    return pd.DataFrame(rows)


# -------------------------------
# 2. SAVE DATA IN SESSION STATE
# -------------------------------

if "complaints_df" not in st.session_state:
    saved_data = load_complaints()

    if saved_data.empty:
        saved_data = create_demo_data()
        save_complaints(saved_data)

    st.session_state.complaints_df = saved_data

df = st.session_state.complaints_df.copy()
df["Date"] = pd.to_datetime(df["Date"])
''

# -------------------------------
# 2. SIDEBAR FILTERS
# -------------------------------
st.sidebar.title("🏙️ Smart City Insights")
st.sidebar.caption("Smart City Analytics Platform")

ward_options = sorted(df["Ward"].unique())
problem_options = sorted(df["Problem"].unique())

selected_wards = st.sidebar.multiselect(
    "Select Ward",
    ward_options,
    default=ward_options
)

selected_problems = st.sidebar.multiselect(
    "Select Problem",
    problem_options,
    default=problem_options
)

selected_status = st.sidebar.multiselect(
    "Select Status",
    ["Resolved", "Pending", "In Progress"],
    default=["Resolved", "Pending", "In Progress"]
)

# ---------------------------------
# ADD A NEW CITY COMPLAINT
# ---------------------------------
st.subheader("📝 Report a City Problem")

with st.form("complaint_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        new_ward = st.selectbox(
            "Select Area",
            [f"Ward {i}" for i in range(1, 9)]
        )

        new_problem = st.selectbox(
            "Problem Type",
            [
                "Garbage",
                "Water Supply",
                "Traffic",
                "Pollution",
                "Street Light"
            ]
        )

        new_date = st.date_input(
            "Complaint Date",
            value=date.today()
        )

    with col2:
        new_severity = st.selectbox(
            "Severity",
            ["Low", "Medium", "High"]
        )

        new_description = st.text_input(
            "Short Description (optional)",
            max_chars=200
        )

    submitted = st.form_submit_button(
        "Submit Complaint"
    )

    if submitted:
        new_row = {
            "Complaint_ID": (
                f"USER{len(st.session_state.complaints_df) + 1:04d}"
            ),
            "Date": pd.Timestamp(new_date),
            "Ward": new_ward,
            "Problem": new_problem,
            "Status": "Pending",
            "Severity": new_severity,
            "Description": new_description
        }

        st.session_state.complaints_df = pd.concat(
            [
                st.session_state.complaints_df,
                pd.DataFrame([new_row])
            ],
            ignore_index=True
        )
        save_complaints(st.session_state.complaints_df)
        st.success("Complaint added successfully!")
        st.rerun()

# Refresh data after a new submission
df = st.session_state.complaints_df.copy()
df["Date"] = pd.to_datetime(df["Date"])

# ---------------------------------
# STEP 10.1: SEARCH COMPLAINT
# ---------------------------------
st.subheader("🔎 Search Complaint")

search_id = st.text_input(
    "Enter Complaint ID",
    placeholder="Example: USER0001 or CP0001"
)

if search_id.strip():
    search_result = st.session_state.complaints_df[
        st.session_state.complaints_df["Complaint_ID"]
        .astype(str)
        .str.contains(
            search_id.strip(),
            case=False,
            na=False
        )
    ]

    if not search_result.empty:
        st.success(
            f"{len(search_result)} complaint(s) found"
        )
        st.dataframe(
            search_result,
            use_container_width=True
        )
    else:
        st.warning("Complaint not found. Please check the ID.")

# ---------------------------------
# STEP 10.2: ADVANCED ANALYTICS
# ---------------------------------

st.subheader("📊 Advanced Complaint Analytics")

analytics_df = st.session_state.complaints_df.copy()
analytics_df["Date"] = pd.to_datetime(analytics_df["Date"])

if not analytics_df.empty:

    # 1. Daily complaint trend
    daily_data = (
        analytics_df.groupby(
            analytics_df["Date"].dt.date
        )
        .size()
        .reset_index(name="Complaints")
    )

    fig_trend = px.line(
        daily_data,
        x="Date",
        y="Complaints",
        title="Daily Complaint Trend",
        markers=True
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # 2. Severity analysis
    severity_data = (
        analytics_df["Severity"]
        .value_counts()
        .reset_index()
    )
    severity_data.columns = ["Severity", "Count"]

    fig_severity = px.bar(
        severity_data,
        x="Severity",
        y="Count",
        color="Severity",
        title="Complaints by Severity"
    )
    st.plotly_chart(fig_severity, use_container_width=True)

else:
    st.info("No complaints available for analytics.")

# -------------------------------
# 3. FILTER DATA
# -------------------------------
filtered = df[
    df["Ward"].isin(selected_wards)
    & df["Problem"].isin(selected_problems)
    & df["Status"].isin(selected_status)
].copy()

# -------------------------------
# PROFESSIONAL KPI DASHBOARD
# -------------------------------
st.title("🏙️ Smart City Insights")
# ADMIN LOGOUT BUTTON
st.sidebar.success("Admin Logged In")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()
# PROFESSIONAL KPI DASHBOARD
st.subheader("📊 City Performance Overview")

total = len(df)
pending = (df["Status"] == "Pending").sum()
progress = (df["Status"] == "In Progress").sum()
resolved = (df["Status"] == "Resolved").sum()

resolution_rate = resolved / total * 100 if total else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Complaints", total)
col2.metric("Pending Complaints", pending)
col3.metric("In Progress", progress)
col4.metric("Resolution Rate", f"{resolution_rate:.1f}%")

# -------------------------------
# STEP 13: PROFESSIONAL ANALYTICS CHARTS
# -------------------------------

st.divider()
st.subheader("📈 Complaint Analytics")

chart_col1, chart_col2 = st.columns(2)

# Chart 1: Complaints by Problem Type
with chart_col1:
    problem_data = df["Problem"].value_counts().reset_index()
    problem_data.columns = ["Problem", "Count"]

    fig_problem = px.bar(
        problem_data,
        x="Problem",
        y="Count",
        color="Count",
        title="Complaints by Problem Type",
        template="plotly_white"
    )
    fig_problem.update_layout(showlegend=False)
    st.plotly_chart(fig_problem, use_container_width=True)

# Chart 2: Complaint Status
with chart_col2:
    status_data = df["Status"].value_counts().reset_index()
    status_data.columns = ["Status", "Count"]

    fig_status = px.pie(
        status_data,
        names="Status",
        values="Count",
        hole=0.5,
        title="Complaint Status Distribution",
        template="plotly_white"
    )
    st.plotly_chart(fig_status, use_container_width=True)

    # -------------------------------
    # STEP 14A: WARD-WISE ANALYSIS
    # -------------------------------

    st.divider()
    st.subheader("🏘️ Ward-wise Complaint Analysis")

    ward_data = (
        df.groupby("Ward")
        .size()
        .reset_index(name="Total Complaints")
        .sort_values("Total Complaints", ascending=False)
    )

    fig_ward = px.bar(
        ward_data,
        x="Ward",
        y="Total Complaints",
        color="Total Complaints",
        title="Complaints by Ward",
        template="plotly_white",
        text="Total Complaints"
    )

    fig_ward.update_layout(
        xaxis_title="Ward",
        yaxis_title="Number of Complaints",
        showlegend=False
    )

    st.plotly_chart(fig_ward, use_container_width=True)



# STEP 14B: WARD-WISE COMPLAINT HOTSPOT MAP

st.divider()
st.subheader("📍 Modinagar — Ward-wise Complaint Hotspots")

# Count complaints in each ward
ward_counts = df.groupby("Ward").size().to_dict()

# Approximate demo positions around Modinagar
ward_locations = {
    "Ward 1": [28.8320, 77.5770],
    "Ward 2": [28.8370, 77.5820],
    "Ward 3": [28.8270, 77.5820],
    "Ward 4": [28.8270, 77.5720],
    "Ward 5": [28.8370, 77.5720],
    "Ward 6": [28.8420, 77.5770],
    "Ward 7": [28.8220, 77.5770],
    "Ward 8": [28.8320, 77.5870]
}

city_map = folium.Map(
    location=[28.832, 77.577],
    zoom_start=14,
    tiles="OpenStreetMap"
)

for ward, coords in ward_locations.items():
    count = int(ward_counts.get(ward, 0))

    folium.CircleMarker(
        location=coords,
        radius=max(8, min(25, 8 + count / 10)),
        popup=f"{ward}: {count} complaints",
        tooltip=f"{ward} — {count} complaints",
        color="red" if count >= 50 else "blue",
        fill=True,
        fill_opacity=0.7
    ).add_to(city_map)

st_folium(
    city_map,
    height=550,
    use_container_width=True
)

# Ward-wise complaint count table
st.subheader("📊 Ward-wise Complaint Count")

ward_summary = (
    df.groupby("Ward")
    .size()
    .reset_index(name="Total Complaints")
    .sort_values("Total Complaints", ascending=False)
)

st.dataframe(
    ward_summary,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Note: Ward marker locations are approximate demo positions, "
    "not verified official ward boundaries."
)


# -------------------------------
# STEP 15: SMART CITY INSIGHTS
# -------------------------------

st.divider()
st.subheader("🤖 CityPulse AI — Smart Insights")

if not df.empty:
    # Most reported problem
    problem_counts = df["Problem"].value_counts()
    top_problem = problem_counts.idxmax()
    top_problem_count = int(problem_counts.max())

    # Ward with most complaints
    ward_counts = df["Ward"].value_counts()
    top_ward = ward_counts.idxmax()
    top_ward_count = int(ward_counts.max())

    # Pending complaints
    pending_count = int((df["Status"] == "Pending").sum())

    # High severity complaints
    high_count = int((df["Severity"] == "High").sum())

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            f"🚨 **Most reported issue:** {top_problem} "
            f"({top_problem_count} complaints)"
        )

        st.warning(
            f"📍 **Priority ward:** {top_ward} "
            f"({top_ward_count} complaints)"
        )

    with col2:
        st.info(
            f"⏳ **Pending complaints:** {pending_count}"
        )

        st.warning(
            f"🔴 **High severity complaints:** {high_count}"
        )

    st.success(
        f"💡 **Suggested action:** Review {top_ward} first "
        f"and investigate the main issue: {top_problem}."
    )

else:
    st.info("No complaint data available yet.")

    # -------------------------------
    # STEP 16: UPDATE COMPLAINT STATUS
    # -------------------------------

    st.divider()
    st.subheader("📝 Update Complaint Status")

    complaints_data = st.session_state.complaints_df

    if not complaints_data.empty:
        complaint_ids = complaints_data["Complaint_ID"].astype(str).tolist()

        selected_id = st.selectbox(
            "Select Complaint ID",
            complaint_ids,
            key="status_complaint_id"
        )

        selected_row = complaints_data[
            complaints_data["Complaint_ID"].astype(str) == selected_id
            ]

        current_status = selected_row.iloc[0]["Status"]

        st.write(f"Current Status: **{current_status}**")

        new_status = st.selectbox(
            "Choose New Status",
            ["Pending", "In Progress", "Resolved"],
            index=["Pending", "In Progress", "Resolved"].index(current_status),
            key="new_complaint_status"
        )

        if st.button("💾 Save Status", key="save_complaint_status"):
            st.session_state.complaints_df.loc[
                st.session_state.complaints_df["Complaint_ID"].astype(str)
                == selected_id,
                "Status"
            ] = new_status

            save_complaints(st.session_state.complaints_df)

            st.success(f"Complaint {selected_id} updated to {new_status}!")
            st.rerun()
    else:
        st.info("No complaints available to update.")


# STEP 11: SIDEBAR NAVIGATION
st.sidebar.title("🏙️ Smart City Insights")
st.sidebar.caption("Smart City Management")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Report a Complaint",
        "Search Complaint",
        "Advanced Analytics",
        "About Project"
    ],
    key="main_navigation"
)
st.sidebar.write("Selected page:", page)
st.sidebar.divider()
st.sidebar.info("Smart City • Better Services")


# PAGE 1: DASHBOARD
if page == "Dashboard":
    st.title("📊 City Dashboard")
    st.caption("Smart City Complaint Analytics Dashboard")

    total_complaints = len(filtered)
    pending_complaints = (filtered["Status"] == "Pending").sum()
    in_progress = (filtered["Status"] == "In Progress").sum()
    resolved_complaints = (filtered["Status"] == "Resolved").sum()

    resolution_rate = (
        resolved_complaints / total_complaints * 100
        if total_complaints > 0 else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("📋 Total Complaints", total_complaints)
    col2.metric("⏳ Pending", int(pending_complaints))
    col3.metric("🔧 In Progress", int(in_progress))
    col4.metric("✅ Resolved", int(resolved_complaints))
    col5.metric("📈 Resolution Rate", f"{resolution_rate:.1f}%")

    st.divider()
    st.info(
        "Dashboard overview. Apne existing charts, ward analysis, "
        "map aur Smart Insights ka code bhi isi Dashboard section "
        "ke andar rakho."
    )


# PAGE 2: REPORT A COMPLAINT
elif page == "Report a Complaint":
    st.title("📝 Report a Complaint")
    st.write("Enter the details of the city complaint below.")

    with st.form("report_complaint_form"):
        ward = st.selectbox(
            "Select Ward",
            [f"Ward {i}" for i in range(1, 9)]
        )

        problem = st.selectbox(
            "Problem Category",
            [
                "Garbage",
                "Water Supply",
                "Traffic",
                "Pollution",
                "Street Light"
            ]
        )

        severity = st.selectbox(
            "Severity",
            ["Low", "Medium", "High"]
        )

        complaint_date = st.date_input("Complaint Date")
        description = st.text_area("Complaint Description")

        submitted = st.form_submit_button(
            "📩 Submit Complaint",
            use_container_width=True
        )

    if submitted:
        if not description.strip():
            st.error("Please enter a complaint description.")
        else:
            st.success(
                "Form submitted successfully. Database saving "
                "needs to be connected to your existing save function."
            )
            st.write("**Ward:**", ward)
            st.write("**Problem:**", problem)
            st.write("**Severity:**", severity)
            st.write("**Date:**", complaint_date)
            st.write("**Description:**", description)


# PAGE 3: SEARCH COMPLAINT
elif page == "Search Complaint":
    st.title("🔎 Search Complaint")
    st.write("Search the existing complaint records.")

    complaint_id = st.text_input("Enter Complaint ID")

    if st.button("Search", use_container_width=True):
        if "Complaint_ID" not in filtered.columns:
            st.error("Complaint ID column was not found.")
        elif not complaint_id.strip():
            st.warning("Please enter a Complaint ID.")
        else:
            result = filtered[
                filtered["Complaint_ID"].astype(str).str.strip()
                == complaint_id.strip()
            ]

            if result.empty:
                st.warning("No complaint found with this ID.")
            else:
                st.success("Complaint found!")
                st.dataframe(result, use_container_width=True)


# PAGE 4: ADVANCED ANALYTICS
elif page == "Advanced Analytics":
    st.title("📈 Advanced Analytics")
    st.caption("Explore complaint trends and service performance.")

    if filtered.empty:
        st.info("No complaint data is available for analysis.")
    else:
        # Problem-wise Analytics
        st.subheader("📊 Complaint Analysis by Problem")
        problem_counts = filtered["Problem"].value_counts()
        st.bar_chart(problem_counts)

        # Status Analytics
        st.subheader("📌 Complaints by Status")
        status_counts = filtered["Status"].value_counts()
        st.bar_chart(status_counts)

        # Ward Analytics
        if "Ward" in filtered.columns:
            st.subheader("🏙️ Ward-wise Complaint Analysis")
            ward_counts = filtered["Ward"].value_counts()
            st.bar_chart(ward_counts)

        # Severity Analytics
        if "Severity" in filtered.columns:
            st.subheader("⚠️ Severity Distribution")
            severity_counts = filtered["Severity"].value_counts()
            st.bar_chart(severity_counts)

        # Complaint Records
        st.subheader("📋 Complaint Records")
        st.dataframe(filtered, use_container_width=True)



# PAGE 5: ABOUT PROJECT
elif page == "About Project":
    st.title("ℹ️ About Smart City Insights")

    st.write(
        " Smart City Insights a smart-city complaint management and "
        "analytics prototype designed to organize civic complaints "
        "and make their status easier to monitor."
    )

    st.subheader("🎯 Main Objectives")
    st.markdown(
        "- Record and organize city complaints.\n"
        "- Track Pending, In Progress and Resolved complaints.\n"
        "- Analyze complaints by ward, category and severity.\n"
        "- Display complaint statistics using charts.\n"
        "- Store complaint records using SQLite."
    )

    st.subheader("🛠️ Technologies Used")
    st.markdown(
        "- **Python:** Application logic\n"
        "- **Streamlit:** Web interface\n"
        "- **Pandas:** Data processing\n"
        "- **Plotly:** Interactive charts in existing dashboard sections\n"
        "- **Folium:** Map visualization\n"
        "- **SQLite:** Local database"
    )

    st.subheader("💡 Smart Insights")
    st.write(
        "The current prototype uses data-based rules and statistics "
        "to highlight complaint patterns. It does not yet use a "
        "trained AI prediction model."
    )

    st.caption("CityPulse AI • Smart City • Better Services")

# -------------------------------
# WARD-WISE ANALYTICS
# -------------------------------
st.subheader("📍 Ward-wise Complaint Analysis")

if not filtered.empty:
    ward_counts = (
        filtered.groupby("Ward")
        .size()
        .reset_index(name="Total Complaints")
        .sort_values("Total Complaints", ascending=False)
    )

    ward_fig = px.bar(
        ward_counts,
        x="Ward",
        y="Total Complaints",
        color="Total Complaints",
        text="Total Complaints",
        title="Complaints by Ward"
    )

    st.plotly_chart(ward_fig, use_container_width=True)
else:
    st.info("No complaints available for this selection.")

    # -------------------------------
    # UPDATE COMPLAINT STATUS
    # -------------------------------
    st.subheader("🛠️ Update Complaint Status")

    if not filtered.empty:
        complaint_ids = filtered["Complaint_ID"].tolist()

        selected_id = st.selectbox(
            "Select Complaint ID",
            complaint_ids
        )

        new_status = st.selectbox(
            "Choose New Status",
            ["Pending", "In Progress", "Resolved"]
        )

        if st.button("Update Status"):
            st.session_state.complaints_df.loc[
                st.session_state.complaints_df["Complaint_ID"] == selected_id,
                "Status"
            ] = new_status

            # Database me bhi save hoga
            save_complaints(st.session_state.complaints_df)

            st.success(f"{selected_id} updated to {new_status}")
            st.rerun()

    # -------------------------------
    # STEP 8: SMART INSIGHTS
    # -------------------------------
    st.subheader("🤖 CityPulse AI - Smart Insights")

    if not filtered.empty:
        total = len(filtered)

        pending = (filtered["Status"] == "Pending").sum()
        resolved = (filtered["Status"] == "Resolved").sum()

        resolution_rate = (resolved / total) * 100

        problem_counts = filtered["Problem"].value_counts()
        ward_counts = filtered["Ward"].value_counts()

        top_problem = problem_counts.idxmax()
        top_problem_count = int(problem_counts.max())

        top_ward = ward_counts.idxmax()
        top_ward_count = int(ward_counts.max())

        col1, col2 = st.columns(2)

        with col1:
            st.info(
                f"📌 Most reported problem: {top_problem} "
                f"({top_problem_count} complaints)"
            )

            st.warning(
                f"⏳ Pending complaints: {pending}"
            )

        with col2:
            st.info(
                f"📍 Ward with most complaints: {top_ward} "
                f"({top_ward_count} complaints)"
            )

            st.success(
                f"✅ Resolution rate: {resolution_rate:.1f}%"
            )

        st.markdown("### 💡 Suggested Action")

        if pending > resolved:
            st.write(
                "Pending complaints resolved cases se zyada hain. "
                "Team ko pending complaints par priority deni chahiye."
            )
        else:
            st.write(
                "Resolved complaints pending complaints ke barabar "
                "ya zyada hain. Pending cases ko monitor karte rahein."
            )

    else:
        st.info("Insights dekhne ke liye complaints available nahi hain.")

# -------------------------------
# 4. PRIORITY SCORING
# -------------------------------
problem_counts = filtered.groupby(
    "Ward"
).size().to_dict()

filtered["Priority_Score"] = (
    filtered["Ward"].map(problem_counts).fillna(0)
)

def get_priority(row):
    if row["Severity"] == "High" and row["Priority_Score"] >= 10:
        return "High"
    elif row["Priority_Score"] >= 10:
        return "Medium"
    return "Low"

filtered["Priority"] = filtered.apply(
    get_priority, axis=1
)

# -------------------------------
# 5. PAGE HEADER
# -------------------------------
st.title("🏙️ CityPulse AI")
st.subheader("Smart City Problem Intelligence Dashboard")
st.caption(
    "Explore complaints, identify problem hotspots "
    "and generate data-driven recommendations."
)

st.info(
    "Demo mode: this dashboard uses synthetic sample data, "
    "not verified live city records."
)

# -------------------------------
# 6. KEY PERFORMANCE INDICATORS
# -------------------------------
total = len(filtered)

resolved = (filtered["Status"] == "Resolved").sum()
pending = (filtered["Status"] == "Pending").sum()
in_progress = (filtered["Status"] == "In Progress").sum()

resolution_rate = (
    resolved / total * 100 if total else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Complaints", f"{total:,}")
c2.metric("Resolved", f"{resolved:,}")
c3.metric("Pending", f"{pending:,}")
c4.metric("Resolution Rate", f"{resolution_rate:.1f}%")

st.divider()

# -------------------------------
# 7. CHARTS
# -------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Complaints by Problem")

    if not filtered.empty:
        problem_chart = (
            filtered.groupby("Problem")
            .size()
            .reset_index(name="Complaints")
            .sort_values("Complaints", ascending=False)
        )

        fig = px.bar(
            problem_chart,
            x="Problem",
            y="Complaints",
            color="Problem",
            title="Which problems occur most?"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data for selected filters.")

with right:
    st.subheader("Ward-wise Problem Hotspots")

    if not filtered.empty:
        ward_chart = (
            filtered.groupby("Ward")
            .size()
            .reset_index(name="Complaints")
            .sort_values("Complaints", ascending=False)
        )

        fig2 = px.bar(
            ward_chart,
            x="Ward",
            y="Complaints",
            color="Complaints",
            title="Complaints by ward"
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data for selected filters.")

# -------------------------------
# 8. COMPLAINT TREND
# -------------------------------
st.subheader("Complaint Trend Over Time")

if not filtered.empty:
    trend = (
        filtered.groupby("Date")
        .size()
        .reset_index(name="Complaints")
        .sort_values("Date")
    )

    fig3 = px.line(
        trend,
        x="Date",
        y="Complaints",
        markers=True,
        title="Daily complaint trend"
    )

    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No trend data available.")

# -------------------------------
# 9. AUTOMATIC DATA INSIGHTS

# --------------------------------
# CITY HOTSPOT MAP - MODINAGAR
# --------------------------------

st.subheader("🗺️ City Hotspot Map - Modinagar")

# Approximate town center
modinagar_center = [28.8321, 77.5771]

# Illustrative points, not official ward boundaries
ward_locations = {
    "Ward 1": [28.8321, 77.5771],
    "Ward 2": [28.8370, 77.5810],
    "Ward 3": [28.8270, 77.5730],
    "Ward 4": [28.8410, 77.5700],
    "Ward 5": [28.8240, 77.5840],
    "Ward 6": [28.8350, 77.5650],
    "Ward 7": [28.8190, 77.5780],
    "Ward 8": [28.8450, 77.5860],
}

city_map = folium.Map(
    location=modinagar_center,
    zoom_start=14,
    tiles="OpenStreetMap"
)

# Display markers based on filtered complaints
if not filtered.empty:
    hotspot_data = (
        filtered.groupby("Ward")
        .size()
        .reset_index(name="Complaints")
    )

    max_count = max(
        int(hotspot_data["Complaints"].max()), 1
    )

    for _, row in hotspot_data.iterrows():
        ward = row["Ward"]
        count = int(row["Complaints"])

        if ward not in ward_locations:
            continue

        if count >= max_count * 0.7:
            color = "red"
        elif count >= max_count * 0.4:
            color = "orange"
        else:
            color = "green"

        folium.CircleMarker(
            location=ward_locations[ward],
            radius=8 + 12 * count / max_count,
            tooltip=f"{ward}: {count} complaints",
            popup=f"{ward} - {count} complaints",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(city_map)

st_folium(
    city_map,
    height=450,
    use_container_width=True
)

st.caption(
    "Demo hotspot map. Locations are illustrative, "
    "not verified official ward coordinates."
)

# -------------------------------
# 10. COMPLAINT TABLE + CSV EXPORT
# -------------------------------
st.subheader("📋 Complaint Records")

if not filtered.empty:
    display_columns = [
        "Complaint_ID", "Date", "Ward", "Problem",
        "Status", "Severity", "Priority"
    ]

    st.dataframe(
        filtered[display_columns].sort_values(
            "Date", ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered[display_columns].to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=csv_data,
        file_name="citypulse_complaints.csv",
        mime="text/csv"
    )
else:
    st.info("No complaint records match your filters.")

st.divider()
st.caption(
    "CityPulse AI | College Mini Project | "
    "Python • Pandas • Plotly • Streamlit"
)
