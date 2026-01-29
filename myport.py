import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from streamlit_calendar import calendar

# =============================
# PAGE CONFIG + THEME
# =============================
st.set_page_config(
    page_title="Academic Progress Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# GLOBAL STYLING (CSS)
# =============================
st.markdown(
    """
    <style>
    .main { background-color: #9bc4eb; }
    .block-container { padding-top: 1.5rem; }
    h1, h2, h3 { color: #1f2a44; }
    .stMetric { background: white; padding: 15px; border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# SESSION STATE INIT
# =============================
if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "email": "",
        "programme": ""
    }

if "semesters" not in st.session_state:
    st.session_state.semesters = {}

if "achievements" not in st.session_state:
    st.session_state.achievements = []

if "events" not in st.session_state:
    st.session_state.events = []

# =============================
# HELPER FUNCTIONS
# =============================
def calculate_weighted_average(df):
    if df.empty:
        return 0
    if "Weight" in df.columns and df["Weight"].sum() > 0:
        return (df["Mark"] * df["Weight"]).sum() / df["Weight"].sum()
    return df["Mark"].mean()


def performance_label(avg):
    if avg >= 70:
        return "🟢 Strong"
    elif avg >= 50:
        return "🟡 Needs Attention"
    return "🔴 At Risk"


def study_tip(avg):
    if avg >= 70:
        return "Maintain consistency and start revision early."
    elif avg >= 50:
        return "Focus on weak topics and practice active recall."
    return "Book consultations, create a strict study plan, and revise fundamentals."

# =============================
# SIDEBAR NAVIGATION (IMPROVED)
# =============================
st.sidebar.markdown("## 🎓 Academic Tracker")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👤 Profile",
        "📚 Semesters & Modules",
        "📊 Achievements",
        "🗓️ Calendar",
        "🤖 Assistant",
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("Phase 1 • Streamlit Academic App")

# =============================
# DASHBOARD
# =============================
if page == "🏠 Dashboard":
    st.title("Academic Dashboard")

    all_averages = []

    for semester, modules in st.session_state.semesters.items():
        for mod, df in modules.items():
            all_averages.append(calculate_weighted_average(df))

    col1, col2 = st.columns(2)

    with col1:
        if all_averages:
            overall = sum(all_averages) / len(all_averages)
            st.metric("Overall Average", f"{overall:.2f}%")
            st.success(performance_label(overall))
        else:
            st.warning("No academic data yet")

    with col2:
        st.metric("Total Modules", len(all_averages))

# =============================
# PROFILE
# =============================
elif page == "👤 Profile":
    st.title("Student Profile")

    st.session_state.profile["name"] = st.text_input("Full Name", st.session_state.profile["name"])
    st.session_state.profile["email"] = st.text_input("Email", st.session_state.profile["email"])
    st.session_state.profile["programme"] = st.text_input("Programme", st.session_state.profile["programme"])

    st.success("Profile saved")

# =============================
# SEMESTERS & MODULES
# =============================
elif page == "📚 Semesters & Modules":
    st.title("Semesters & Modules")

    semester = st.text_input("Semester Name")
    if st.button("Create / Load Semester") and semester:
        st.session_state.semesters.setdefault(semester, {})

    if semester in st.session_state.semesters:
        module = st.text_input("Module Name")
        if st.button("Add Module") and module:
            st.session_state.semesters[semester].setdefault(
                module,
                pd.DataFrame(columns=["Assessment", "Mark", "Weight"])
            )

        for mod, df in st.session_state.semesters[semester].items():
            st.subheader(mod)

            with st.form(f"form_{semester}_{mod}"):
                assessment = st.text_input("Assessment")
                mark = st.number_input("Mark", 0.0, 100.0)
                weight = st.number_input("Weight", 0.0, 1.0)
                submit = st.form_submit_button("Add Assessment")

            if submit:
                df.loc[len(df)] = [assessment, mark, weight]

            st.dataframe(df, use_container_width=True)

            avg = calculate_weighted_average(df)
            st.metric("Module Average", f"{avg:.2f}%", performance_label(avg))
            st.info(study_tip(avg))

            if not df.empty:
                fig, ax = plt.subplots()
                ax.plot(df["Assessment"], df["Mark"], marker="o")
                ax.set_ylim(0, 100)
                ax.set_title("Performance Trend")
                st.pyplot(fig)

# =============================
# ACHIEVEMENTS
# =============================
elif page == "📊 Achievements":
    st.title("Achievements")

    with st.form("achievement_form"):
        title = st.text_input("Title")
        date = st.date_input("Date", datetime.date.today())
        desc = st.text_area("Description")
        submit = st.form_submit_button("Add")

    if submit:
        st.session_state.achievements.append({
            "title": title,
            "date": date,
            "description": desc
        })
        st.success("Achievement added")

    for ach in st.session_state.achievements:
        st.markdown(f"### 🏆 {ach['title']}")
        st.caption(ach['date'])
        st.write(ach['description'])

# =============================
# CALENDAR (API-BASED)
# =============================
elif page == "🗓️ Calendar":
    st.title("Academic Calendar")

    with st.form("event_form"):
        title = st.text_input("Event")
        date = st.date_input("Date")
        submit = st.form_submit_button("Add Event")

    if submit:
        st.session_state.events.append({
            "title": title,
            "start": date.isoformat(),
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "height": 600,
    }

    calendar(events=st.session_state.events, options=calendar_options)

# =============================
# ASSISTANT
# =============================
elif page == "🤖 Assistant":
    st.title("Academic Assistant")

    q = st.text_input("Ask about your academics")

    if q:
        if "focus" in q.lower():
            st.write("Focus on modules marked 🔴 At Risk.")
        elif "average" in q.lower():
            st.write("Your performance updates automatically as you add marks.")
        else:
            st.write("I can help you analyse performance trends and priorities.")

