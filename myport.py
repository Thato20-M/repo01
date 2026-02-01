import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import datetime
from streamlit_calendar import calendar

# =============================
# 🔥 KEEP ML + LLM IMPORTS
# =============================
from ml.feature_engineering import build_features
from ml.predictor import AcademicPredictor
from services.context_builder import build_llm_context
from services.assistant import generate_llm_prompt


def get_conn():
    return sqlite3.connect("academic.db", check_same_thread=False)

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Academic Progress Tracker",
    page_icon="🎓",
    layout="wide"
)

# =============================
# DATABASE (PERSISTENT)
# =============================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        programme TEXT,
        photo BLOB
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        semester TEXT,
        module TEXT,
        assessment TEXT,
        mark REAL,
        weight REAL
    )
    """)

    conn.commit()
    conn.close()


init_db()

# =============================
# GLOBAL STYLING
# =============================
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #f4f6fb, #5199c2);
}
h1, h2, h3 {
    color: #1f2a44;
}
.card {
    background: #1F2A44;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
.metric {
    font-size: 38px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =============================
# HELPERS
# =============================
def weighted_average(df):
    if df.empty:
        return 0
    if df["weight"].sum() > 0:
        return (df["mark"] * df["weight"]).sum() / df["weight"].sum()
    return df["mark"].mean()

def risk_label(avg):
    if avg >= 70:
        return "🟢 Low Risk"
    elif avg >= 50:
        return "🟡 Medium Risk"
    return "🔴 High Risk"

# =============================
# SIDEBAR
# =============================
st.sidebar.title("🎓 Academic Tracker")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "👤 Profile",
        "📚 Modules",
        "📈 Trends",
        "🤖 Assistant"
    ]
)

# =============================
# DASHBOARD
# =============================
if page == "📊 Dashboard":
    st.title("Academic Overview")

    conn = get_conn()
    df = pd.read_sql("SELECT * FROM assessments", conn)
    conn.close()

    if df.empty:
        st.info("No academic data yet.")
    else:
        overall_avg = weighted_average(df)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="card">
                <h3>Overall Average</h3>
                <div class="metric">{overall_avg:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <h3>Risk Status</h3>
                <div class="metric">{risk_label(overall_avg)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="card">
                <h3>Total Assessments</h3>
                <div class="metric">{len(df)}</div>
            </div>
            """, unsafe_allow_html=True)
#--------------------------------
#Profile
#-------------------------------
elif page == "👤 Profile":
    st.title("Student Profile")

    conn = get_conn()
    cur = conn.cursor()

    # Load profile
    cur.execute(
        "SELECT name, email, programme, photo FROM profiles WHERE id = 1"
    )
    row = cur.fetchone()

    name, email, programme, photo = row if row else ("", "", "", None)

    # Profile picture
    profile_pic = st.file_uploader(
        "Upload Profile Picture",
        type=["png", "jpg", "jpeg"]
    )

    if photo:
        st.image(photo, width=150)

    # Profile fields
    name = st.text_input("Full Name", name)
    email = st.text_input("Email", email)
    programme = st.text_input("Programme", programme)

    if st.button("Save Profile"):
        if name and email and programme:
            cur.execute("""
                INSERT OR REPLACE INTO profiles
                (id, name, email, programme, photo)
                VALUES (1, ?, ?, ?, ?)
            """, (
                name,
                email,
                programme,
                profile_pic.read() if profile_pic else photo
            ))

            conn.commit()
            st.success("✅ Profile saved successfully")
        else:
            st.warning("Please complete all profile fields")

    conn.close()

# =============================
# MODULE ENTRY
# =============================
elif page == "📚 Modules":
    st.title("Modules & Assessments")

    semester = st.text_input("Semester")
    module = st.text_input("Module")

    with st.form("assessment_form"):
        assessment = st.text_input("Assessment Name")
        mark = st.number_input("Mark", 0.0, 100.0)
        weight = st.number_input("Weight (0–1)", 0.0, 1.0)
        submit = st.form_submit_button("Save Assessment")

    if submit and semester and module:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO assessments (semester, module, assessment, mark, weight)
            VALUES (?, ?, ?, ?, ?)
        """, (semester, module, assessment, mark, weight))
        conn.commit()
        conn.close()
        st.success("Assessment saved")

    if semester and module:
        conn = get_conn()
        df = pd.read_sql("""
            SELECT assessment, mark, weight
            FROM assessments
            WHERE semester=? AND module=?
        """, conn, params=(semester, module))
        conn.close()

        if not df.empty:
            avg = weighted_average(df)
            st.metric("Module Average", f"{avg:.2f}%", risk_label(avg))
            st.dataframe(df, use_container_width=True)

# =============================
# TRENDS
# =============================
elif page == "📈 Trends":
    st.title("Performance Trends")

    conn = get_conn()
    df = pd.read_sql("SELECT * FROM assessments", conn)
    conn.close()

    if df.empty:
        st.warning("No data to visualize.")
    else:
        trend = (
            df.groupby("semester")
              .apply(weighted_average)
              .reset_index(name="Average")
        )

        fig, ax = plt.subplots()
        ax.plot(trend["semester"], trend["Average"], marker="o")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Average (%)")
        ax.set_title("Academic Performance Over Semesters")
        st.pyplot(fig)

# =============================
# ASSISTANT (ML + LLM)
# =============================
elif page == "🤖 Assistant":
    st.title("Academic Assistant")

    # -------------------------------
    # LOAD DATA
    # -------------------------------
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM assessments", conn)
    profile_df = pd.read_sql(
        "SELECT name, programme FROM profiles WHERE id = 1",
        conn
    )
    conn.close()

    profile = {
        "name": profile_df.iloc[0]["name"] if not profile_df.empty else "Student",
        "degree": profile_df.iloc[0]["programme"] if not profile_df.empty else ""
    }

    achievements = []
    events = []
    predictions = {}

    # -------------------------------
    # BUILD PREDICTIONS (SAFE)
    # -------------------------------
    if not df.empty:
        features = build_features(df)
        predictor = AcademicPredictor()

        next_mark, risk_prob = predictor.predict(features)

        predictions["Overall"] = {
            "next_mark": float(next_mark),
            "risk_prob": float(risk_prob)
        }

   
