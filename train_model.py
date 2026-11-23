
import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


# 1. Load student dataset
DATA_PATH = "data/synthetic_training_students.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print("Total students:", len(df))


# 2. Select academic features
features = [
    "Attendance",
    "Internal_Marks",
    "Assignment_Score",
    "Previous_SGPA",
    "Backlogs",
    "Lab_Marks",
    "Class_Participation"
]

targets = ["Final_Grade", "Risk_Level"]

required_columns = features + targets

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(
        f"Missing columns in dataset: {missing}"
    )


# 3. Preprocessing
X = df[features].copy()

X["Class_Participation"] = (
    X["Class_Participation"]
    .map({"Low": 0, "Medium": 1, "High": 2})
)

for col in features:
    X[col] = pd.to_numeric(X[col], errors="coerce")

y_grade = df["Final_Grade"]
y_risk = df["Risk_Level"]


# 4. Use the same train/test split for both targets
indices = df.index.to_numpy()

train_idx, test_idx = train_test_split(
    indices,
    test_size=0.2,
    random_state=42
)

X_train = X.loc[train_idx]
X_test = X.loc[test_idx]


# 5. Create models
def create_model():
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            random_state=42
        ))
    ])


grade_model = create_model()
risk_model = create_model()


# 6. Train grade prediction model
grade_model.fit(
    X_train,
    y_grade.loc[train_idx]
)

grade_predictions = grade_model.predict(X_test)

print("\nFINAL GRADE PREDICTION")
print(
    "Accuracy:",
    round(
        accuracy_score(
            y_grade.loc[test_idx],
            grade_predictions
        ) * 100,
        2
    ),
    "%"
)

print(
    classification_report(
        y_grade.loc[test_idx],
        grade_predictions,
        zero_division=0
    )
)


# 7. Train academic risk prediction model
risk_model.fit(
    X_train,
    y_risk.loc[train_idx]
)

risk_predictions = risk_model.predict(X_test)

print("\nACADEMIC RISK PREDICTION")
print(
    "Accuracy:",
    round(
        accuracy_score(
            y_risk.loc[test_idx],
            risk_predictions
        ) * 100,
        2
    ),
    "%"
)

print(
    classification_report(
        y_risk.loc[test_idx],
        risk_predictions,
        zero_division=0
    )
)


# 8. Save trained models
os.makedirs("models", exist_ok=True)

joblib.dump(
    grade_model,
    "models/grade_model.pkl"
)

joblib.dump(
    risk_model,
    "models/risk_model.pkl"
)

print("\nModels saved successfully!")
print("models/grade_model.pkl")
print("models/risk_model.pkl")
# 9. Save model evaluation results

evaluation = {
    "Grade Prediction": {
        "accuracy": accuracy_score(
            y_grade.loc[test_idx],
            grade_predictions
        ),
        "report": classification_report(
            y_grade.loc[test_idx],
            grade_predictions,
            output_dict=True,
            zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            y_grade.loc[test_idx],
            grade_predictions
        ).tolist(),
        "labels": grade_model.classes_.tolist()
    },
    "Academic Risk Prediction": {
        "accuracy": accuracy_score(
            y_risk.loc[test_idx],
            risk_predictions
        ),
        "report": classification_report(
            y_risk.loc[test_idx],
            risk_predictions,
            output_dict=True,
            zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            y_risk.loc[test_idx],
            risk_predictions
        ).tolist(),
        "labels": risk_model.classes_.tolist()
    }
}

joblib.dump(
    evaluation,
    "models/evaluation.pkl"
)

print("Model evaluation saved successfully!")