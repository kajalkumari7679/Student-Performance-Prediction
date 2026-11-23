
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)

records = []
courses = ["MCA", "BCA", "B.Tech", "MBA"]
participation_levels = ["Low", "Medium", "High"]

for i in range(1, 1001):
    course = rng.choice(courses)

    max_year = {
        "MCA": 2,
        "BCA": 3,
        "B.Tech": 4,
        "MBA": 2
    }[course]

    year = int(rng.integers(1, max_year + 1))
    semester = int(rng.choice([2 * year - 1, 2 * year]))

    attendance = int(rng.integers(45, 101))
    internal = int(rng.integers(5, 31))
    assignment = int(rng.integers(3, 21))
    lab = int(rng.integers(5, 31))
    sgpa = round(float(rng.uniform(4, 10)), 2)
    backlogs = int(rng.choice(
        [0, 1, 2, 3],
        p=[0.65, 0.20, 0.10, 0.05]
    ))
    participation = str(rng.choice(participation_levels))

    # Demonstration score (not official university grading)
    score = (
        0.30 * (internal / 30 * 100)
        + 0.20 * (assignment / 20 * 100)
        + 0.25 * (lab / 30 * 100)
        + 0.15 * (sgpa * 10)
        + 0.10 * attendance
    )

    score += {"Low": -3, "Medium": 0, "High": 3}[participation]
    score -= backlogs * 3
    score += rng.normal(0, 4)
    score = float(np.clip(score, 0, 100))

    if score >= 90:
        grade = "O"
    elif score >= 80:
        grade = "A+"
    elif score >= 70:
        grade = "A"
    elif score >= 60:
        grade = "B+"
    elif score >= 50:
        grade = "B"
    elif score >= 40:
        grade = "C"
    else:
        grade = "F"

    # Illustrative academic-support categories
    if attendance < 60 or backlogs >= 3 or score < 40:
        risk = "High Risk"
    elif attendance < 75 or backlogs >= 1 or score < 60:
        risk = "Moderate Risk"
    else:
        risk = "Low Risk"

    records.append({
        "Student_Name": f"Demo Student {i:04d}",
        "Roll_No": f"DEMO/{course}/{i:04d}/26",
        "Course": course,
        "Year": year,
        "Semester": semester,
        "Academic_Session": "2026-2027",
        "Attendance": attendance,
        "Internal_Marks": internal,
        "Assignment_Score": assignment,
        "Previous_SGPA": sgpa,
        "Backlogs": backlogs,
        "Lab_Marks": lab,
        "Class_Participation": participation,
        "Final_Grade": grade,
        "Risk_Level": risk
    })

df = pd.DataFrame(records)

Path("data").mkdir(exist_ok=True)

output_path = "data/synthetic_training_students.csv"
df.to_csv(output_path, index=False)

print("Synthetic dataset created successfully!")
print("Total students:", len(df))
print("\nGrade distribution:")
print(df["Final_Grade"].value_counts())
print("\nRisk distribution:")
print(df["Risk_Level"].value_counts())
print("\nSaved to:", output_path)
