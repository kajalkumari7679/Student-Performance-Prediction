
import sqlite3
import pandas as pd

DB_NAME = "students.db"


def get_connection():
    return sqlite3.connect(DB_NAME, timeout=10)


def create_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                Roll_No TEXT PRIMARY KEY,
                Student_Name TEXT NOT NULL,
                Course TEXT,
                Year INTEGER,
                Semester INTEGER,
                Academic_Session TEXT,
                Attendance REAL,
                Internal_Marks REAL,
                Assignment_Score REAL,
                Previous_SGPA REAL,
                Backlogs INTEGER,
                Lab_Marks REAL,
                Class_Participation TEXT
            )
        """)


def add_student(student):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO students (
                Roll_No, Student_Name, Course, Year,
                Semester, Academic_Session, Attendance,
                Internal_Marks, Assignment_Score,
                Previous_SGPA, Backlogs, Lab_Marks,
                Class_Participation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student["Roll_No"],
            student["Student_Name"],
            student["Course"],
            student["Year"],
            student["Semester"],
            student["Academic_Session"],
            student["Attendance"],
            student["Internal_Marks"],
            student["Assignment_Score"],
            student["Previous_SGPA"],
            student["Backlogs"],
            student["Lab_Marks"],
            student["Class_Participation"]
        ))


def get_students():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM students ORDER BY Roll_No",
            conn
        )


def search_student(roll_no):
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM students WHERE Roll_No = ?",
            conn,
            params=(roll_no,)
        )


def update_student(roll_no, updates):
    allowed_columns = {
        "Student_Name", "Course", "Year", "Semester",
        "Academic_Session", "Attendance", "Internal_Marks",
        "Assignment_Score", "Previous_SGPA", "Backlogs",
        "Lab_Marks", "Class_Participation"
    }

    updates = {
        key: value
        for key, value in updates.items()
        if key in allowed_columns
    }

    if not updates:
        return

    fields = ", ".join(
        f"{column} = ?" for column in updates
    )

    values = list(updates.values()) + [roll_no]

    with get_connection() as conn:
        conn.execute(
            f"UPDATE students SET {fields} WHERE Roll_No = ?",
            values
        )


def delete_student(roll_no):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM students WHERE Roll_No = ?",
            (roll_no,)
        )


if __name__ == "__main__":
    create_database()
    print("Student database created successfully!")
