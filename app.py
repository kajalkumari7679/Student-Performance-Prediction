

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


st.title("🎓 Student Performance Prediction")
st.subheader("👩‍🏫 Faculty Academic Dashboard")

st.write(
    "Analyze student attendance, academic performance "
    "and class records using CSV or Excel files."
)


# Manage Students - Manual Entry

st.divider()
st.header("👩‍🏫 Manage Students")

with st.form("add_student_form", clear_on_submit=True):
    st.subheader("➕ Add New Student")

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

    if submitted:
        if not student_name.strip() or not roll_no.strip():
            st.warning("Enter Student Name and Roll Number.")
        else:
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



# Search Student from Database

st.divider()
st.header("🔍 Search Student")

search_roll = st.text_input(
    "Enter Roll Number to Search",
    key="search_roll"
)

if st.button("Search Student"):
    if search_roll.strip():
        students = get_students()

        result = students[
            students["Roll_No"].astype(str).str.strip()
            == search_roll.strip()
        ]

        if not result.empty:
            st.success("Student Found!")
            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Student not found in database.")
    else:
        st.warning("Please enter a Roll Number.")



# Edit Student Details

st.divider()
st.header("✏️ Edit Student Details")

edit_roll = st.text_input(
    "Enter Roll Number to Edit",
    key="edit_roll"
)

students = get_students()

matching_students = students[
    students["Roll_No"].astype(str).str.strip()
    == edit_roll.strip()
] if edit_roll.strip() else pd.DataFrame()

if not matching_students.empty:
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

            st.success("Student details updated successfully!")
            st.rerun()



# Delete Student from Database

st.divider()
st.header("🗑️ Delete Student")

delete_roll = st.text_input(
    "Enter Roll Number to Delete",
    key="delete_roll"
)

if delete_roll.strip():
    students = get_students()

    matching = students[
        students["Roll_No"].astype(str).str.strip()
        == delete_roll.strip()
    ]

    if not matching.empty:
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
            st.success("Student deleted successfully!")
            st.rerun()
    else:
        st.info("No matching student found in database.")



# Teacher Dashboard - Class Student Records

st.divider()
st.header("👩‍🏫 Teacher Dashboard")
st.subheader("Class Student Records")

uploaded_file = st.file_uploader(
    "Upload Student Excel or CSV File",
    type=["csv", "xlsx"],
    key="class_upload"
)

try:
    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".xlsx"):
            class_data = pd.read_excel(uploaded_file)
        else:
            class_data = pd.read_csv(uploaded_file)
    else:
        class_data = pd.read_csv("data/sample_students.csv")


       # Load students from SQLite database   
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



    st.success("Student records loaded successfully!")

    st.metric("Total Students", len(class_data))

    # Course, Year and Semester filters
    filtered_data = class_data.copy()

    for column in ["Course", "Year", "Semester"]:
        if column in filtered_data.columns:
            options = sorted(
                filtered_data[column].dropna().unique().tolist(),
                key=str
            )

            selected = st.multiselect(
                f"Filter by {column}",
                options,
                default=options
            )

            filtered_data = filtered_data[
                filtered_data[column].isin(selected)
            ]

    st.dataframe(
        filtered_data,
        use_container_width=True,
        hide_index=True
    )


    # Teacher Dashboard - Academic Risk Analysis

    st.divider()
    st.subheader("📊 Academic Risk Analysis")

    if "Attendance" in filtered_data.columns:

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
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "📥 Download Attendance Shortage Report",
            data=shortage_students.to_csv(index=False),
            file_name="attendance_shortage_report.csv",
            mime="text/csv"
        )

    else:
        st.info(
            "Attendance column not found in the uploaded sheet."
        )



    # Teacher Dashboard - Class Analytics

    st.divider()
    st.subheader("📈 Class Analytics")

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



    st.download_button(
        "📥 Download Student Records",
        data=filtered_data.to_csv(index=False),
        file_name="student_records.csv",
        mime="text/csv"
    )

except FileNotFoundError:
    st.error(
        "Sample dataset not found. "
        "Check data/sample_students.csv"
    )



# ML Prediction for CSV, Excel and Database Students

st.divider()
st.header("🎯 Student Performance Prediction")

st.write(
    "Select a student from uploaded records "
    "or the SQLite database."
)

try:
    grade_model = joblib.load("models/grade_model.pkl")
    risk_model = joblib.load("models/risk_model.pkl")

    # Use the same records shown in Teacher Dashboard
    if "class_data" in locals():
        students = class_data.copy()
    else:
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

    elif students.empty:
        st.info("No student records available.")

    else:
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

        if st.button("🔮 Predict Performance"):

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
                use_container_width=True,
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

except FileNotFoundError:
    st.error(
        "ML model files not found. "
        "Run python3 train_model.py first."
    )


# Model Evaluation Dashboard

st.divider()
st.header("📊 Model Evaluation Dashboard")

try:
    evaluation = joblib.load("models/evaluation.pkl")

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
            use_container_width=True
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
            use_container_width=True
        )

    st.caption(
        "Evaluation uses held-out synthetic test data. "
        "Results do not establish accuracy on real students."
    )

except FileNotFoundError:
    st.warning(
        "Evaluation file not found. Run python3 train_model.py first."
    )
