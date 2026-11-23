# Student Performance Prediction Using Machine Learning

## Project Overview

This university minor project explores student performance analysis using Python and machine learning. It contains two related but distinct workflows:

1. **Exploratory analysis and mathematics-score modelling** using the Expanded Student Performance dataset and a command-line Python script.
2. **Faculty Academic Dashboard** built with Streamlit, using a demonstration dataset and a local SQLite database to manage student records, analyze class performance, predict final-grade categories and academic-risk categories, and download student reports.

The workflows use different datasets, targets and model evaluations. Their results must not be compared as if they were produced by the same model or test set.

## Objectives

- Explore patterns in student academic records through data preprocessing and visualizations.
- Train and evaluate educational demonstration models for academic outcomes.
- Provide a teacher-facing interface for adding, searching, updating and deleting student records.
- Support CSV/Excel upload and class-level attendance and performance analysis.
- Display predictions and evaluation metrics with clear limitations.

## Technologies

Python, pandas, NumPy, scikit-learn, Streamlit, SQLite (`sqlite3`), joblib, and, for the exploratory analysis workflow, Matplotlib and Seaborn. Visual Studio Code is an optional editor.

## Project Components

### A. Exploratory Data Analysis and Mathematics Score Modelling

**Main script:** `student_performance.py`  
**Dataset:** `Expanded_data_with_more_features.csv`

The original analysis uses the Expanded Student Performance dataset (reported as 30,641 rows and 15 original columns). It examines academic scores and student-related attributes such as parental education, weekly study hours, test preparation and sports participation.

- **Linear Regression:** Predicts `MathScore` using `ReadingScore`, `WritingScore` and `NrSiblings`.
- **Random Forest Classifier:** Classifies grade categories A, B, C, D and F using selected student-related attributes.
- **Outputs:** Exploratory charts, confusion matrix, actual-versus-predicted visualization and result CSVs.

**Previously reported results for this separate workflow:**

| Metric | Reported result |
| --- | ---: |
| Linear Regression mean squared error | 79.08 |
| Linear Regression R² | 0.6648 |
| Random Forest classification accuracy | 36.42% |
| Classification test samples | 6,129 |

These figures are from the earlier analysis and are not results from the Streamlit dashboard models. They should be rechecked by rerunning that script before submission.

### B. Streamlit Faculty Academic Dashboard

**Main app:** `app.py`  
**Database module:** `database.py`  
**Training script:** `train_model.py`  
**Synthetic data generator:** `generate_dataset.py`

Dashboard features:

- Add, search, edit and delete student records using local SQLite storage.
- Upload class records in CSV or Excel (`.xlsx`) format.
- Display the provided sample class records and combine them with locally saved database records, prioritizing database entries when roll numbers overlap.
- Filter records by course, year and semester.
- Flag attendance below a demonstration threshold of 75% and export a shortage report.
- Visualize attendance distribution, previous SGPA distribution and attendance versus internal marks.
- Select a student and predict **Final Grade** and **Academic Risk**.
- Display and download a student performance report as CSV.
- Show model accuracy, confusion matrices and classification reports.

## Dashboard Data and Machine Learning

The dashboard uses `data/sample_students.csv` as its default display dataset (100 fictional student records) and `data/synthetic_training_students.csv` for training (1,000 synthetic records in the current implementation). New records entered through the form are stored in a local `students.db` SQLite file.

The dashboard models are separate **Random Forest Classifier** pipelines with median-value imputation. Both use these input features:

`Attendance`, `Internal_Marks`, `Assignment_Score`, `Previous_SGPA`, `Backlogs`, `Lab_Marks`, `Class_Participation`.

Class participation is encoded as Low = 0, Medium = 1, High = 2. The two targets are `Final_Grade` and `Risk_Level`. The training script uses an 80/20 train/test split with `random_state=42`.

**Previously observed dashboard model results (held-out synthetic test data):**

| Model | Observed accuracy |
| --- | ---: |
| Final Grade classification | 55.00% |
| Academic Risk classification | 94.00% |

The app loads current evaluation artifacts from `models/evaluation.pkl`; the dashboard should be treated as the authoritative display after retraining. These figures **do not validate performance on real student records**. In particular, grade classification performance is limited.

## Suggested Project Folder Structure

```text
Student_Performance_Prediction/
├── app.py
├── database.py
├── train_model.py
├── generate_dataset.py
├── student_performance.py              # Separate EDA workflow
├── Expanded_data_with_more_features.csv # Separate EDA dataset
├── requirements.txt
├── README.md
├── data/
│   ├── sample_students.csv
│   └── synthetic_training_students.csv
├── models/
│   ├── grade_model.pkl
│   ├── risk_model.pkl
│   └── evaluation.pkl
└── students.db                         # Created locally; do not commit real records
```

The structure describes the files used by the two workflows; verify the filenames and their presence in your own folder before submitting.

## Installation and Execution (macOS)

Open a terminal in the project folder, where `app.py` is located.

**1. Create and activate a virtual environment (recommended):**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**2. Install dependencies:**

```bash
python3 -m pip install -r requirements.txt
```

Ensure `requirements.txt` includes the libraries imported by the dashboard and training script (`streamlit`, `pandas`, `scikit-learn`, `joblib`, and `openpyxl` for Excel uploads). The separate EDA workflow also needs `numpy`, `matplotlib`, and `seaborn`. Install missing dependencies before running either workflow.

**3. Prepare the training data, if needed:**

```bash
python3 generate_dataset.py
```

This step is only needed when `data/synthetic_training_students.csv` has not yet been generated or needs to be regenerated.

**4. Train the dashboard models and save evaluation results:**

```bash
python3 train_model.py
```

This should generate `models/grade_model.pkl`, `models/risk_model.pkl`, and `models/evaluation.pkl` when using the updated training script.

**5. Launch the Streamlit dashboard:**

```bash
python3 -m streamlit run app.py
```

Open the local URL printed in the terminal (usually `http://localhost:8501`). To request the previously used port 8503:

```bash
python3 -m streamlit run app.py --server.port 8503
```

**Optional: Run the separate exploratory analysis:**

```bash
python3 -u student_performance.py
```

For that workflow, keep `Expanded_data_with_more_features.csv` at the location expected by the script and inspect its generated images and CSV files.

## How to Use the Dashboard

1. In **Manage Students**, add a fictional student record, or upload a CSV/Excel class sheet in **Teacher Dashboard**.
2. Search, edit or delete locally saved records by roll number.
3. Explore course/year/semester filters, attendance shortage and class analytics.
4. In **Student Performance Prediction**, select a roll number and click **Predict Performance**.
5. Review the predicted grade and risk category, then download the student's report if needed.
6. Inspect the **Model Evaluation Dashboard** for the saved test-set accuracy, confusion matrix and classification report.

## Limitations and Responsible Use

- The Streamlit models are trained and evaluated on **synthetic data**, not validated institutional records. Predictions must not be used for admissions, grading, disciplinary action or other consequential academic decisions.
- The dashboard grade model's observed 55% accuracy is insufficient for reliable student-level assessment.
- The earlier EDA workflow's 36.42% grade classification accuracy is also limited.
- The EDA regression uses reading and writing scores to estimate mathematics scores, so it is not a forecast before those scores are known.
- Attendance/marks visualizations show associations, not causation.
- Local SQLite data is stored on the machine running the app. On ephemeral hosting, local database records may be lost; a persistent managed database would be required for durable cloud use.
- The current demonstration has no production authentication, role-based access control or comprehensive privacy safeguards. Use fictional data only until these controls are implemented.

## Future Scope

- Evaluate on appropriately consented, representative real-world data with privacy protections.
- Improve grade-model features, calibration and evaluation across student groups.
- Add secure faculty authentication and access controls.
- Use a persistent database for cloud deployment.
- Provide downloadable PDF reports and clearer model-explanation views.
- Add automated tests and reproducible model/version metadata.

## Conclusion 
This project combines exploratory academic data analysis with a Streamlit-based faculty dashboard. It demonstrates student-record management, data visualization, classification pipelines, prediction reports and model evaluation. All prediction outputs are educational demonstrations, and the two workflows' datasets and metrics are documented separately to avoid misleading conclusions.
