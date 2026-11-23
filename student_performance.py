
# Import Libraries
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score

# Load Dataset
df = pd.read_csv("Expanded_data_with_more_features.csv")

print("Dataset Loaded Successfully!")

# First Five Rows
print("\nFirst Five Rows:")
print(df.head())

# Dataset Shape
print("\nDataset Shape:", df.shape)

# Dataset Information
print("\nDataset Information:")
df.info()

# Descriptive Statistics
print("\nDescriptive Statistics:")
print(df.describe())

# Missing Values
print("\nMissing Values:")
print(df.isnull().sum())

# Remove Unnecessary Column
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

print("\nData Preprocessing Completed!")


# ===================================
# PART 2: DESCRIPTIVE STATISTICS
# ===================================

columns = ['MathScore', 'ReadingScore',
           'WritingScore', 'NrSiblings']

mean = df[columns].mean()
median = df[columns].median()
mode = df[columns].mode()
std_dev = df[columns].std()

print("\nMean:\n", mean)
print("\nMedian:\n", median)
print("\nMode:\n", mode)
print("\nStandard Deviation:\n", std_dev)


# ===================================
# PART 3: CORRELATION ANALYSIS
# ===================================

corr = df[['MathScore', 'ReadingScore',
           'WritingScore']].corr()

print("\nCorrelation Matrix:")
print(corr)

plt.figure(figsize=(8, 6))

sns.heatmap(
    corr,
    annot=True,
    cmap='coolwarm',
    fmt='.2f'
)

plt.title("Correlation Between Student Scores")
plt.tight_layout()
plt.savefig("correlation_heatmap.png")
plt.close()


# ===================================
# PART 4: GENDER DISTRIBUTION
# ===================================

plt.figure(figsize=(6, 5))

ax = sns.countplot(
    data=df,
    x="Gender"
)

for container in ax.containers:
    ax.bar_label(container)

plt.title("Gender Distribution of Students")
plt.xlabel("Gender")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.savefig("gender_distribution.png")
plt.close()


# ==========================================
# PART 6: LINEAR REGRESSION MODEL
# ==========================================

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

print("\n--- LINEAR REGRESSION MODEL ---")

# Select input features and target
features = [
    "ReadingScore",
    "WritingScore",
    "NrSiblings"
]

# Remove rows with missing values
reg_df = df[features + ["MathScore"]].dropna()

X = reg_df[features]
y = reg_df["MathScore"]

# Split dataset into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create Linear Regression model
lr_model = LinearRegression()

# Train model
lr_model.fit(X_train, y_train)

# Predict Math Scores
y_pred = lr_model.predict(X_test)

y_test_lr = y_test.copy()
y_pred_lr = y_pred.copy()

# Evaluate model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Mean Squared Error:", mse)
print("R2 Score:", r2)

# Compare actual and predicted scores
results = pd.DataFrame({
    "Actual Score": y_test.values,
    "Predicted Score": y_pred
})

print("\nActual vs Predicted Scores:")
print(results.head(10))

# Save results
results.to_csv("linear_regression_results.csv", index=False)

print("\nLinear Regression Completed Successfully!")



# ==========================================
# PART 7: IMPROVED RANDOM FOREST MODEL
# ==========================================

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report

print("\n--- IMPROVED RANDOM FOREST ---")

features = [
    "Gender",
    "ParentEduc",
    "LunchType",
    "TestPrep",
    "ParentMaritalStatus",
    "PracticeSport",
    "WklyStudyHours"
]

# Prepare dataset
clf_df = df.dropna(subset=["MathScore"]).copy()

# Create grades from Math Score
bins = [-float("inf"), 60, 70, 80, 90, float("inf")]
labels = ["F", "D", "C", "B", "A"]

clf_df["Grade"] = pd.cut(
    clf_df["MathScore"],
    bins=bins,
    labels=labels
)

X = clf_df[features]
y = clf_df["Grade"]

# Handle missing categorical values
preprocessor = ColumnTransformer([
    ("categorical", Pipeline([
        ("imputer", SimpleImputer(
            strategy="most_frequent"
        )),
        ("encoder", OneHotEncoder(
            handle_unknown="ignore"
        ))
    ]), features)
])

# Create model pipeline
rf_model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    ))
])

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Train model
rf_model.fit(X_train, y_train)

# Predict grades
y_pred = rf_model.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)

print("Improved Model Accuracy:", accuracy * 100, "%")

print("\nClassification Report:")
print(classification_report(
    y_test, y_pred, zero_division=0
))

# Save predictions
results = pd.DataFrame({
    "Actual Grade": y_test.to_numpy(),
    "Predicted Grade": y_pred
})

results.to_csv(
    "improved_random_forest_results.csv",
    index=False
)

# ==========================================
# PART 8: NEW STUDENT PREDICTION
# ==========================================

print("\n--- NEW STUDENT PREDICTION ---")

new_student = pd.DataFrame([{
    "Gender": "female",
    "ParentEduc": "bachelor's degree",
    "LunchType": "standard",
    "TestPrep": "completed",
    "ParentMaritalStatus": "married",
    "PracticeSport": "regularly",
    "WklyStudyHours": "5 - 10"
}])

predicted_grade = rf_model.predict(new_student)

print("Predicted Student Grade:", predicted_grade[0])


# ==========================================
# PART 9: CONFUSION MATRIX
# ==========================================

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

print("\n--- CONFUSION MATRIX ---")

# Create confusion matrix
cm = confusion_matrix(
    y_test,
    y_pred,
    labels=rf_model.classes_
)

# Plot confusion matrix
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=rf_model.classes_
)

disp.plot(cmap="Blues", values_format="d")

plt.title("Student Grade Prediction - Confusion Matrix")
plt.tight_layout()

# Save graph
plt.savefig("confusion_matrix.png", dpi=300)
plt.show(block=False)
plt.pause(2)
plt.close()

print("Confusion Matrix Saved Successfully!")

plt.savefig("confusion_matrix.png")
plt.show()
plt.close()


# ==========================================
# PART 10: ACTUAL VS PREDICTED SCORES
# ==========================================

print("\n--- FINAL MODEL EVALUATION ---")

plt.figure(figsize=(8, 6))

plt.scatter(
    y_test_lr,
    y_pred_lr,
    alpha=0.5,
    color="blue"
)

plt.plot(
    [0, 100],
    [0, 100],
    color="red",
    linestyle="--",
    label="Perfect Prediction"
)

plt.xlabel("Actual Math Score")
plt.ylabel("Predicted Math Score")
plt.title("Actual vs Predicted Student Math Scores")
plt.legend()
plt.grid(True)

plt.savefig("actual_vs_predicted.png", dpi=300)
plt.show(block=False)
plt.pause(2)
plt.close()

print("Actual vs Predicted Graph Saved!")


# ==========================================
# PART 11: SAVE TRAINED MODEL
# ==========================================

import joblib

joblib.dump(rf_model, "student_model.pkl", compress=3)

print("\nModel Saved Successfully!")
