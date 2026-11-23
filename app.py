from database import create_database, add_student, get_students, update_student, delete_student
import sqlite3
import streamlit as st
import pandas as pd
import joblib

st.set_page_config(
    page_title="Student Performance Prediction",
    page_icon="🎓",
    layout="wide"
)

create_database()


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
#
# The tabs below are "lazy": only the selected tab's code runs. Streamlit
# discards the value of any widget that is not drawn in a run, so state that
# must survive switching tabs (the uploaded class file, the class filters and
# success messages shown after st.rerun) is kept in st.session_state.

SAMPLE_DATA_PATH = "data/sample_students.csv"
FILTER_COLUMNS = ["Course", "Year", "Semester"]


def set_flash(message):
    """Store a success message to show after st.rerun()."""
    st.session_state["flash_message"] = message


def show_flash():
    message = st.session_state.pop("flash_message", None)
    if message:
        st.success(message)


def handle_upload():
    """Read a newly uploaded (or removed) class file into session state."""
    uploaded_file = st.session_state.get("class_upload")
    st.session_state.pop("upload_error", None)

    if uploaded_file is None:
        st.session_state.pop("uploaded_class_data", None)
        st.session_state.pop("uploaded_file_name", None)
        return

    try:
        if uploaded_file.name.lower().endswith(".xlsx"):
            data = pd.read_excel(uploaded_file)
        else:
            data = pd.read_csv(uploaded_file)

        st.session_state["uploaded_class_data"] = data
        st.session_state["uploaded_file_name"] = uploaded_file.name
    except Exception as error:
        st.session_state.pop("uploaded_class_data", None)
        st.session_state.pop("uploaded_file_name", None)
        st.session_state["upload_error"] = (
            f"Could not read {uploaded_file.name}: {error}"
        )


def clear_upload():
    st.session_state.pop("uploaded_class_data", None)
    st.session_state.pop("uploaded_file_name", None)
    st.session_state.pop("upload_error", None)


def load_class_data():
    """Uploaded file (or the sample CSV) merged with SQLite records.

    Database entries take priority when roll numbers overlap.
    Raises FileNotFoundError if no file is uploaded and the sample CSV is missing.
    """
    if "uploaded_class_data" in st.session_state:
        class_data = st.session_state["uploaded_class_data"].copy()
    else:
        class_data = pd.read_csv(SAMPLE_DATA_PATH)

    db_students = get_students()

    if not db_students.empty:
        if "Roll_No" in class_data.columns:
            saved_rolls = set(
                db_students["Roll_No"].astype(str).str.strip()
            )

            class_data = class_data[
                ~class_data["Roll_No"]
                .astype(str)
                .str.strip()
                .isin(saved_rolls)
            ]

        class_data = pd.concat(
            [class_data, db_students],
            ignore_index=True
        )

    return class_data


def persistent_filter(column, options):
    """Multiselect whose choice survives switching between tabs.

    The *excluded* values are stored, so options that appear later
    (e.g. a newly added course) are selected by default.
    """
    store_key = f"filter_excluded_{column}"
    widget_key = f"filter_widget_{column}"

    def remember_excluded(shown_options):
        # Runs only when the user changes this filter.
        selected_now = st.session_state.get(widget_key, [])
        st.session_state[store_key] = [
            option for option in shown_options
            if option not in selected_now
        ]

    excluded = st.session_state.get(store_key, [])
    st.session_state[widget_key] = [
        option for option in options if option not in excluded
    ]

    return st.multiselect(
        f"Filter by {column}",
        options,
        key=widget_key,
        on_change=remember_excluded,
        args=(options,)
    )


def render_filters(class_data):
    """Course / Year / Semester filters shared by the class tabs."""
    filtered_data = class_data.copy()
    available = [c for c in FILTER_COLUMNS if c in filtered_data.columns]

    if not available:
        return filtered_data

    with st.expander("🔎 Filters (Course, Year, Semester)", expanded=True):
        columns = st.columns(len(available))

        for container, column in zip(columns, available):
            with container:
                options = sorted(
                    filtered_data[column].dropna().unique().tolist(),
                    key=str
                )
                selected = persistent_filter(column, options)

            filtered_data = filtered_data[
                filtered_data[column].isin(selected)
            ]

    return filtered_data


def load_filtered_data():
    """Class data with the shared filters applied, or None if unavailable."""
    try:
        class_data = load_class_data()
    except FileNotFoundError:
        st.error(
            "Sample dataset not found. "
            f"Check {SAMPLE_DATA_PATH}"
        )
        return None

    if "uploaded_file_name" in st.session_state:
        st.caption(
            f"Data source: {st.session_state['uploaded_file_name']} "
            "+ local database"
        )
    else:
        st.caption(
            "Data source: sample records + local database "
            "(upload your own file in the Class Records tab)"
        )

    return render_filters(class_data)


# ---------------------------------------------------------------------------
# Page header and tabs
# ---------------------------------------------------------------------------

st.title("🎓 Student Performance Prediction")
st.subheader("👩‍🏫 Faculty Academic Dashboard")

st.write(
    "Analyze student attendance, academic performance "
    "and class records using CSV or Excel files."
)

TAB_PREDICTION = "🎯 Performance Prediction"
TAB_ADD = "➕ Add Student"
TAB_SEARCH = "🔍 Search Student"
TAB_EDIT = "✏️ Edit Student"
TAB_DELETE = "🗑️ Delete Student"
TAB_RECORDS = "👩‍🏫 Class Records"
TAB_RISK = "⚠️ Risk Analysis"
TAB_ANALYTICS = "📈 Class Analytics"
TAB_EVALUATION = "📊 Model Evaluation"

TAB_NAMES = [
    TAB_PREDICTION,
    TAB_ADD,
    TAB_SEARCH,
    TAB_EDIT,
    TAB_DELETE,
    TAB_RECORDS,
    TAB_RISK,
    TAB_ANALYTICS,
    TAB_EVALUATION,
]

# on_change="rerun" makes the tabs lazy: only the selected tab's code runs
# and its content is shown. The key keeps the selected tab across reruns.
tabs = dict(zip(
    TAB_NAMES,
    st.tabs(
        TAB_NAMES,
        default=TAB_PREDICTION,
        key="main_tabs",
        on_change="rerun"
    )
))


# ---------------------------------------------------------------------------
# Tab: Student Performance Prediction (front page)
# ---------------------------------------------------------------------------

def render_prediction():
    st.header("🎯 Student Performance Prediction")

    st.write(
        "Select a student from uploaded records "
        "or the SQLite database."
    )

    try:
        grade_model = joblib.load("models/grade_model.pkl")
        risk_model = joblib.load("models/risk_model.pkl")
    except FileNotFoundError:
        st.error(
            "ML model files not found. "
            "Run python3 train_model.py first."
        )
        return

    # Use the same records shown in the Class Records tab
    try:
        students = load_class_data()
    except FileNotFoundError:
        students = get_students()

    required_columns = [
        "Roll_No",
        "Student_Name",
        "Attendance",
        "Internal_Marks",
        "Assignment_Score",
        "Previous_SGPA",
        "Backlogs",
        "Lab_Marks",
        "Class_Participation"
    ]

    missing = [
        col for col in required_columns
        if col not in students.columns
    ]

    if missing:
        st.error(f"Missing columns: {missing}")
        return

    if students.empty:
        st.info("No student records available.")
        return

    students["Roll_No"] = (
        students["Roll_No"].astype(str).str.strip()
    )

    students = students.drop_duplicates(
        subset=["Roll_No"],
        keep="last"
    )

    selected_roll = st.selectbox(
        "Select Student Roll Number",
        students["Roll_No"].tolist(),
        key="prediction_roll"
    )

    student = students[
        students["Roll_No"] == selected_roll
    ].iloc[0]

    st.write(
        "**Student Name:**",
        student["Student_Name"]
    )

    if "Course" in student.index:
        st.write("**Course:**", student["Course"])

    if not st.button("🔮 Predict Performance"):
        return

    features = pd.DataFrame([{
        "Attendance": student["Attendance"],
        "Internal_Marks": student["Internal_Marks"],
        "Assignment_Score": student["Assignment_Score"],
        "Previous_SGPA": student["Previous_SGPA"],
        "Backlogs": student["Backlogs"],
        "Lab_Marks": student["Lab_Marks"],
        "Class_Participation": {
            "Low": 0,
            "Medium": 1,
            "High": 2
        }.get(
            str(student["Class_Participation"]).strip(),
            None
        )
    }])

    numeric_columns = [
        "Attendance",
        "Internal_Marks",
        "Assignment_Score",
        "Previous_SGPA",
        "Backlogs",
        "Lab_Marks"
    ]

    for column in numeric_columns:
        features[column] = pd.to_numeric(
            features[column],
            errors="coerce"
        )

    grade = grade_model.predict(features)[0]
    risk = risk_model.predict(features)[0]

    col1, col2 = st.columns(2)

    col1.metric(
        "Predicted Final Grade",
        grade
    )

    col2.metric(
        "Predicted Academic Risk",
        risk
    )

    # Student Performance Report
    report = student.to_frame().T.copy()

    report["Predicted_Final_Grade"] = grade
    report["Predicted_Academic_Risk"] = risk

    st.subheader("📄 Student Performance Report")

    st.dataframe(
        report,
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "📥 Download Student Performance Report",
        data=report.to_csv(index=False),
        file_name=f"performance_report_{selected_roll.replace('/', '_')}.csv",
        mime="text/csv"
    )

    st.caption(
        "Demonstration predictions based on "
        "synthetic training data. Not validated "
        "for real academic decisions."
    )


# ---------------------------------------------------------------------------
# Tab: Add Student
# ---------------------------------------------------------------------------

def render_add_student():
    st.header("➕ Add New Student")

    with st.form("add_student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            student_name = st.text_input("Student Name")
            roll_no = st.text_input("Roll Number")
            course = st.selectbox(
                "Course", ["MCA", "BCA", "B.Tech", "MBA"]
            )
            year = st.selectbox(
                "Year", [1, 2, 3, 4]
            )
            semester = st.selectbox(
                "Semester", list(range(1, 9))
            )

        with col2:
            attendance = st.number_input(
                "Attendance (%)", 0.0, 100.0, 75.0
            )
            internal_marks = st.number_input(
                "Internal Marks (out of 30)", 0, 30, 15
            )
            assignment_score = st.number_input(
                "Assignment Score (out of 20)", 0, 20, 10
            )
            lab_marks = st.number_input(
                "Lab Marks (out of 30)", 0, 30, 15
            )
            previous_sgpa = st.number_input(
                "Previous SGPA", 0.0, 10.0, 6.0
            )
            backlogs = st.number_input(
                "Active Backlogs", 0, 20, 0
            )

        participation = st.selectbox(
            "Class Participation", ["Low", "Medium", "High"]
        )

        academic_session = st.text_input(
            "Academic Session", "2026-2027"
        )

        submitted = st.form_submit_button("Save Student")

    if not submitted:
        return

    if not student_name.strip() or not roll_no.strip():
        st.warning("Enter Student Name and Roll Number.")
        return

    new_student = pd.DataFrame([{
        "Student_Name": student_name.strip(),
        "Roll_No": roll_no.strip(),
        "Course": course,
        "Year": year,
        "Semester": semester,
        "Academic_Session": academic_session,
        "Attendance": attendance,
        "Internal_Marks": internal_marks,
        "Assignment_Score": assignment_score,
        "Previous_SGPA": previous_sgpa,
        "Backlogs": backlogs,
        "Lab_Marks": lab_marks,
        "Class_Participation": participation
    }])

    try:
        add_student(new_student.iloc[0].to_dict())
        st.success(
            "Student saved permanently in local database!"
        )
        st.dataframe(new_student, hide_index=True)

    except sqlite3.IntegrityError:
        st.error(
            "This Roll Number already exists. "
            "Please enter a unique Roll Number."
        )


# ---------------------------------------------------------------------------
# Tab: Search Student
# ---------------------------------------------------------------------------

def render_search_student():
    st.header("🔍 Search Student")

    search_roll = st.text_input(
        "Enter Roll Number to Search",
        key="search_roll"
    )

    if not st.button("Search Student"):
        return

    if not search_roll.strip():
        st.warning("Please enter a Roll Number.")
        return

    students = get_students()

    result = students[
        students["Roll_No"].astype(str).str.strip()
        == search_roll.strip()
    ]

    if not result.empty:
        st.success("Student Found!")
        st.dataframe(
            result,
            width="stretch",
            hide_index=True
        )
    else:
        st.warning("Student not found in database.")


# ---------------------------------------------------------------------------
# Tab: Edit Student
# ---------------------------------------------------------------------------

def render_edit_student():
    st.header("✏️ Edit Student Details")
    show_flash()

    edit_roll = st.text_input(
        "Enter Roll Number to Edit",
        key="edit_roll"
    )

    if not edit_roll.strip():
        return

    students = get_students()

    matching_students = students[
        students["Roll_No"].astype(str).str.strip()
        == edit_roll.strip()
    ]

    if matching_students.empty:
        st.info("No matching student found in database.")
        return

    student = matching_students.iloc[0]

    st.info(f"Editing: {student['Student_Name']}")

    with st.form("edit_student_form"):
        new_attendance = st.number_input(
            "Update Attendance (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(student["Attendance"])
        )

        new_internal = st.number_input(
            "Update Internal Marks",
            min_value=0,
            max_value=30,
            value=int(student["Internal_Marks"])
        )

        new_assignment = st.number_input(
            "Update Assignment Score",
            min_value=0,
            max_value=20,
            value=int(student["Assignment_Score"])
        )

        new_lab = st.number_input(
            "Update Lab Marks",
            min_value=0,
            max_value=30,
            value=int(student["Lab_Marks"])
        )

        new_sgpa = st.number_input(
            "Update Previous SGPA",
            min_value=0.0,
            max_value=10.0,
            value=float(student["Previous_SGPA"])
        )

        save_changes = st.form_submit_button(
            "💾 Save Changes"
        )

    if save_changes:
        update_student(edit_roll.strip(), {
            "Attendance": new_attendance,
            "Internal_Marks": new_internal,
            "Assignment_Score": new_assignment,
            "Lab_Marks": new_lab,
            "Previous_SGPA": new_sgpa
        })

        set_flash("Student details updated successfully!")
        st.rerun()


# ---------------------------------------------------------------------------
# Tab: Delete Student
# ---------------------------------------------------------------------------

def render_delete_student():
    st.header("🗑️ Delete Student")
    show_flash()

    delete_roll = st.text_input(
        "Enter Roll Number to Delete",
        key="delete_roll"
    )

    if not delete_roll.strip():
        return

    students = get_students()

    matching = students[
        students["Roll_No"].astype(str).str.strip()
        == delete_roll.strip()
    ]

    if matching.empty:
        st.info("No matching student found in database.")
        return

    student = matching.iloc[0]

    st.warning(
        f"Student: {student['Student_Name']} "
        f"(Roll No: {student['Roll_No']})"
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this student."
    )

    if st.button(
        "🗑️ Delete Student Permanently",
        disabled=not confirm_delete
    ):
        delete_student(delete_roll.strip())
        set_flash("Student deleted successfully!")
        st.rerun()


# ---------------------------------------------------------------------------
# Tab: Class Records (Teacher Dashboard)
# ---------------------------------------------------------------------------

def render_class_records():
    st.header("👩‍🏫 Teacher Dashboard")
    st.subheader("Class Student Records")

    st.file_uploader(
        "Upload Student Excel or CSV File",
        type=["csv", "xlsx"],
        key="class_upload",
        on_change=handle_upload
    )

    if "upload_error" in st.session_state:
        st.error(st.session_state["upload_error"])

    if "uploaded_file_name" in st.session_state:
        info_col, button_col = st.columns([4, 1])
        info_col.info(
            f"Using uploaded file: "
            f"**{st.session_state['uploaded_file_name']}** "
            "(stays loaded when you switch tabs)"
        )
        button_col.button(
            "Use sample data instead",
            on_click=clear_upload
        )

    filtered_data = load_filtered_data()

    if filtered_data is None:
        return

    st.success("Student records loaded successfully!")

    st.metric("Total Students", len(filtered_data))

    st.dataframe(
        filtered_data,
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "📥 Download Student Records",
        data=filtered_data.to_csv(index=False),
        file_name="student_records.csv",
        mime="text/csv"
    )


# ---------------------------------------------------------------------------
# Tab: Academic Risk Analysis
# ---------------------------------------------------------------------------

def render_risk_analysis():
    st.header("⚠️ Academic Risk Analysis")

    filtered_data = load_filtered_data()

    if filtered_data is None:
        return

    if "Attendance" not in filtered_data.columns:
        st.info(
            "Attendance column not found in the uploaded sheet."
        )
        return

    analysis_data = filtered_data.copy()

    analysis_data["Attendance"] = pd.to_numeric(
        analysis_data["Attendance"]
            .astype(str)
            .str.replace("%", "", regex=False),
        errors="coerce"
    )

    # Demo attendance shortage threshold
    analysis_data["Attendance_Alert"] = (
        analysis_data["Attendance"].apply(
            lambda x: "Shortage" if pd.notna(x) and x < 75
            else "No Shortage" if pd.notna(x)
            else "Unknown"
        )
    )

    shortage_count = (
        analysis_data["Attendance_Alert"] == "Shortage"
    ).sum()

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Students",
        len(analysis_data)
    )

    col2.metric(
        "Attendance Shortage",
        int(shortage_count)
    )

    st.subheader("Attendance Shortage Students")

    shortage_students = analysis_data[
        analysis_data["Attendance_Alert"] == "Shortage"
    ]

    st.dataframe(
        shortage_students,
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "📥 Download Attendance Shortage Report",
        data=shortage_students.to_csv(index=False),
        file_name="attendance_shortage_report.csv",
        mime="text/csv"
    )


# ---------------------------------------------------------------------------
# Tab: Class Analytics
# ---------------------------------------------------------------------------

def render_class_analytics():
    st.header("📈 Class Analytics")

    filtered_data = load_filtered_data()

    if filtered_data is None:
        return

    analytics_data = filtered_data.copy()

    # Convert academic columns into numeric values
    numeric_columns = [
        "Attendance",
        "Internal_Marks",
        "Assignment_Score",
        "Lab_Marks",
        "Previous_SGPA",
        "Backlogs"
    ]

    for column in numeric_columns:
        if column in analytics_data.columns:
            analytics_data[column] = pd.to_numeric(
                analytics_data[column]
                    .astype(str)
                    .str.replace("%", "", regex=False),
                errors="coerce"
            )

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Students",
        len(analytics_data)
    )

    if "Attendance" in analytics_data.columns:
        avg_attendance = analytics_data["Attendance"].mean()
        col2.metric(
            "Average Attendance",
            f"{avg_attendance:.1f}%"
            if pd.notna(avg_attendance) else "N/A"
        )
    else:
        col2.metric("Average Attendance", "N/A")

    if "Previous_SGPA" in analytics_data.columns:
        avg_sgpa = analytics_data["Previous_SGPA"].mean()
        col3.metric(
            "Average Previous SGPA",
            f"{avg_sgpa:.2f}"
            if pd.notna(avg_sgpa) else "N/A"
        )
    else:
        col3.metric("Average Previous SGPA", "N/A")

    # Attendance distribution
    if "Attendance" in analytics_data.columns:
        st.write("**Attendance Distribution**")

        attendance_groups = pd.cut(
            analytics_data["Attendance"],
            bins=[-0.01, 60, 75, 90, 100],
            labels=[
                "0–60%",
                "60–75%",
                "75–90%",
                "90–100%"
            ],
            include_lowest=True
        )

        attendance_counts = (
            attendance_groups.value_counts()
            .sort_index()
        )

        st.bar_chart(attendance_counts)

    # Previous SGPA distribution
    if "Previous_SGPA" in analytics_data.columns:
        st.write("**Previous Semester SGPA Distribution**")

        st.bar_chart(
            analytics_data["Previous_SGPA"]
                .dropna()
                .round()
                .value_counts()
                .sort_index()
        )

    # Attendance vs Internal Marks
    if all(
        col in analytics_data.columns
        for col in ["Attendance", "Internal_Marks"]
    ):
        st.write("**Attendance vs Internal Marks**")

        st.scatter_chart(
            analytics_data,
            x="Attendance",
            y="Internal_Marks"
        )


# ---------------------------------------------------------------------------
# Tab: Model Evaluation
# ---------------------------------------------------------------------------

def render_model_evaluation():
    st.header("📊 Model Evaluation Dashboard")

    try:
        evaluation = joblib.load("models/evaluation.pkl")
    except FileNotFoundError:
        st.warning(
            "Evaluation file not found. Run python3 train_model.py first."
        )
        return

    for model_name, results in evaluation.items():
        st.subheader(model_name)

        st.metric(
            "Model Accuracy",
            f"{results['accuracy'] * 100:.2f}%"
        )

        st.write("**Confusion Matrix**")

        labels = results["labels"]

        cm = pd.DataFrame(
            results["confusion_matrix"],
            index=labels,
            columns=labels
        )

        st.dataframe(
            cm,
            width="stretch"
        )

        st.caption(
            "Rows = Actual Class | Columns = Predicted Class"
        )

        st.write("**Classification Report**")

        report = pd.DataFrame(
            results["report"]
        ).T

        st.dataframe(
            report,
            width="stretch"
        )

    st.caption(
        "Evaluation uses held-out synthetic test data. "
        "Results do not establish accuracy on real students."
    )


# ---------------------------------------------------------------------------
# Render only the selected tab
# ---------------------------------------------------------------------------

RENDERERS = {
    TAB_PREDICTION: render_prediction,
    TAB_ADD: render_add_student,
    TAB_SEARCH: render_search_student,
    TAB_EDIT: render_edit_student,
    TAB_DELETE: render_delete_student,
    TAB_RECORDS: render_class_records,
    TAB_RISK: render_risk_analysis,
    TAB_ANALYTICS: render_class_analytics,
    TAB_EVALUATION: render_model_evaluation,
}

# Note shown at the bottom of each tab explaining what the page does.
PAGE_NOTES = {
    TAB_PREDICTION: (
        "Pick a student by roll number from the class records (your uploaded "
        "file or the built-in sample, plus students saved in the local "
        "database). **Predict Performance** runs two Random Forest models on "
        "attendance, internal marks, assignment score, previous SGPA, "
        "backlogs, lab marks and class participation, and shows the "
        "predicted **final grade** and **academic risk level**. The result "
        "can be downloaded as a CSV report. The models are trained on "
        "synthetic data, so predictions are for demonstration only."
    ),
    TAB_ADD: (
        "Enter a new student's details and save them to the local SQLite "
        "database (`students.db`). Each roll number must be unique. Saved "
        "students appear in every other tab, and replace any record with the "
        "same roll number in the uploaded or sample file."
    ),
    TAB_SEARCH: (
        "Find a student by their exact roll number. This searches only "
        "students saved in the local database, not the uploaded or sample "
        "file."
    ),
    TAB_EDIT: (
        "Enter the roll number of a student saved in the local database to "
        "update their attendance, internal marks, assignment score, lab marks "
        "and previous SGPA. Other details (name, course, year, etc.) cannot "
        "be changed here."
    ),
    TAB_DELETE: (
        "Permanently remove a student saved in the local database, by roll "
        "number, after ticking the confirmation box. This cannot be undone. "
        "Records in the uploaded or sample file are not affected."
    ),
    TAB_RECORDS: (
        "Shows the full class list: your uploaded CSV/Excel file (or the "
        "built-in sample of 100 fictional students if nothing is uploaded) "
        "combined with students saved in the local database. Narrow it down "
        "by course, year and semester; these filters also apply to the Risk "
        "Analysis and Class Analytics tabs. The filtered list can be "
        "downloaded as CSV."
    ),
    TAB_RISK: (
        "Flags students in the filtered records whose attendance is below "
        "75% (a demonstration threshold), shows how many there are and lists "
        "them, with a downloadable shortage report. This check uses "
        "attendance only, not the prediction models."
    ),
    TAB_ANALYTICS: (
        "Summarises the filtered records: total students, average attendance "
        "and average previous SGPA. The charts show how attendance is spread "
        "across bands, how previous SGPA is spread (rounded to whole "
        "numbers), and attendance plotted against internal marks. The charts "
        "show patterns, not causes."
    ),
    TAB_EVALUATION: (
        "Shows how the two prediction models performed on held-out synthetic "
        "test data when `train_model.py` was last run: overall accuracy, a "
        "confusion matrix (rows = actual class, columns = predicted class) "
        "and a classification report with precision, recall and F1 for each "
        "class. These scores do not measure accuracy on real students."
    ),
}


def page_note(name):
    st.divider()
    st.info(f"**About this page:** {PAGE_NOTES[name]}", icon="ℹ️")


for name, tab in tabs.items():
    if tab.open:
        with tab:
            RENDERERS[name]()
            page_note(name)
