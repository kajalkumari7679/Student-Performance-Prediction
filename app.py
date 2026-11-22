
import streamlit as st
import pandas as pd
import joblib

st.set_page_config(
    page_title="Student Performance Prediction",
    page_icon="🎓"
)

@st.cache_resource
def load_model():
    return joblib.load("student_model.pkl")

model = load_model()

st.title("🎓 Student Performance Prediction")
st.write("Predict student grades using Machine Learning.")

st.subheader("Enter Student Details")

gender = st.selectbox("Gender", ["female", "male"])

parent_educ = st.selectbox(
    "Parent Education",
    ["some high school", "high school", "some college",
     "associate's degree", "bachelor's degree", "master's degree"]
)

lunch = st.selectbox(
    "Lunch Type", ["standard", "free/reduced"]
)

prep = st.selectbox(
    "Test Preparation", ["none", "completed"]
)

marital = st.selectbox(
    "Parent Marital Status",
    ["married", "single", "divorced", "widowed"]
)

sport = st.selectbox(
    "Practice Sport", ["never", "sometimes", "regularly"]
)

hours = st.selectbox(
    "Weekly Study Hours", ["< 5", "5 - 10", "> 10"]
)

if st.button("Predict Student Grade"):
    student = pd.DataFrame([{
        "Gender": gender,
        "ParentEduc": parent_educ,
        "LunchType": lunch,
        "TestPrep": prep,
        "ParentMaritalStatus": marital,
        "PracticeSport": sport,
        "WklyStudyHours": hours
    }])

    grade = model.predict(student)[0]

    st.success(f"Predicted Student Grade: {grade}")
    st.caption(
        "Experimental prediction only. "
        "Model test accuracy: approximately 36.42%."
    )
