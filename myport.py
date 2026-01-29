import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(
    page_title="Academic Progress Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Session State Initialization
# -----------------------------
if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "email": "",
        "programme": ""
    }

if "semesters" not in st.session_state:
    # Structure:
    # {semester_name: {module_name: DataFrame}}
    st.session_state.semesters = {}

if "achievements" not in st.session_state:
    st.session_state.achievements = []

if "events" not in st.session_state:
    st.session_state.events = []

# -----------------------------
# Helper Functions
# -----------------------------

def calculate_weighted_average(df):
    if df.empty:
        return 0
    if "Weight" in df.columns:
        return (df["Mark"] * df["Weight"]).sum() / df["Weight"].sum()
    return df["Mark"].mean()


def performance_trend(avg):
    if avg >= 70:
        return "Strong performance 👍"
    elif avg >= 50:
        return "Stable but needs improvement ⚠️"
    else:
        return "At risk 🚨"


def study_tips(avg):
    if avg >= 70:
        return "Maintain consistency, practice past papers, and help peers."
    elif avg >= 50:
        return "Increase weekly study hours, focus on weak topics, and revise actively."
    else:
        return "Seek academic support, restructure study plan, and prioritize this module."

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Profile", "Semesters & Modules", "Achievements", "Calendar", "Chatbot"]
)

# -----------------------------
# Profile Page
# -----------------------------
if page == "Profile":
    st.title("Student Profile")

    st.session_state.profile["name"] = st.text_input("Full Name", st.session_state.profile["name"])
    st.session_state.profile["email"] = st.text_input("Email", st.session_state.profile["email"])
    st.session_state.profile["programme"] = st.text_input("Degree / Programme", st.session_state.profile["programme"])

    st.success("Profile updated successfully")

# -----------------------------
# Semesters & Modules Page
# -----------------------------
elif page == "Semesters & Modules":
    st.title("Academic Progress Tracking")

    semester = st.text_input("Add / Select Semester")

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

            new_row = st.form(key=f"form_{semester}_{mod}")
            assessment = new_row.text_input("Assessment")
            mark = new_row.number_input("Mark", 0.0, 100.0)
            weight = new_row.number_input("Weight", 0.0, 1.0)
            submitted = new_row.form_submit_button("Add")

            if submitted:
                df.loc[len(df)] = [assessment, mark, weight]

            st.dataframe(df)

            avg = calculate_weighted_average(df)
            st.metric("Module Average", f"{avg:.2f}%")
            st.info(performance_trend(avg))
            st.write("Study Tip:", study_tips(avg))

            if not df.empty:
                fig, ax = plt.subplots()
                ax.plot(df["Assessment"], df["Mark"], marker="o")
                ax.set_ylim(0, 100)
                ax.set_title(f"Performance Trend: {mod}")
                st.pyplot(fig)

# -----------------------------
# Dashboard Page
# -----------------------------
elif page == "Dashboard":
    st.title("Academic Dashboard")

    all_averages = []

    for semester, modules in st.session_state.semesters.items():
        for mod, df in modules.items():
            avg = calculate_weighted_average(df)
            all_averages.append(avg)

    if all_averages:
        overall_avg = sum(all_averages) / len(all_averages)
        st.metric("Overall Academic Average", f"{overall_avg:.2f}%")
        st.success(performance_trend(overall_avg))
    else:
        st.info("No academic data available yet")

# -----------------------------
# Achievements Page
# -----------------------------
elif page == "Achievements":
    st.title("Personal Achievements")

    with st.form("achievement_form"):
        title = st.text_input("Title")
        date = st.date_input("Date", datetime.date.today())
        desc = st.text_area("Description")
        submit = st.form_submit_button("Add Achievement")

    if submit:
        st.session_state.achievements.append({
            "title": title,
            "date": date,
            "description": desc
        })
        st.success("Achievement added")

    for ach in st.session_state.achievements:
        st.subheader(ach["title"])
        st.caption(ach["date"])
        st.write(ach["description"])

# -----------------------------
# Calendar Page
# -----------------------------
elif page == "Calendar":
    st.title("Academic Calendar")

    with st.form("event_form"):
        event = st.text_input("Event")
        date = st.date_input("Date")
        module = st.text_input("Related Module (optional)")
        submit = st.form_submit_button("Add Event")

    if submit:
        st.session_state.events.append({
            "event": event,
            "date": date,
            "module": module
        })
        st.success("Event added")

    for e in sorted(st.session_state.events, key=lambda x: x["date"]):
        st.write(f"📅 {e['date']} — {e['event']} ({e['module']})")

# -----------------------------
# Chatbot Page (Rule-based for v1)
# -----------------------------
elif page == "Chatbot":
    st.title("Academic Assistant")

    query = st.text_input("Ask a question about your academics")

    if query:
        if "semester" in query.lower():
            st.write("You are currently managing", len(st.session_state.semesters), "semester(s).")
        elif "focus" in query.lower():
            st.write("Focus on modules with averages below 50%.")
        elif "achievement" in query.lower():
            st.write("You have", len(st.session_state.achievements), "recorded achievements.")
        else:
            st.write("I can help you analyse your performance and plan better study strategies.")
