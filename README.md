# Student Performance Prediction Using Machine Learning

## 1. Project Overview

This project aims to analyze student academic performance and predict mathematics scores and grade categories using Machine Learning techniques.

The project uses Linear Regression for score prediction and Random Forest Classifier for grade classification.

## 2. Objectives

- Analyze student academic performance.
- Perform data preprocessing and exploratory data analysis.
- Predict mathematics scores using Linear Regression.
- Classify students into grade categories using Random Forest.
- Evaluate model performance using appropriate metrics.
- Visualize results using graphs.

## 3. Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Visual Studio Code

## 4. Dataset

The project uses the Expanded Student Performance dataset.

- Total records: 30,641
- Original columns: 15
- Target variable: MathScore

The dataset includes academic scores and student-related attributes such as parental education, study hours, test preparation, and sports participation.

## 5. Machine Learning Algorithms

### Linear Regression

Linear Regression predicts mathematics scores using reading scores, writing scores, and number of siblings.

### Random Forest Classifier

Random Forest classifies students into five grade categories: A, B, C, D, and F.

It uses student-related features such as gender, parental education, lunch type, test preparation, parental marital status, sports participation, and weekly study hours.

## 6. Project Workflow

1. Dataset loading
2. Data preprocessing
3. Exploratory Data Analysis
4. Data visualization
5. Linear Regression training
6. Random Forest classification
7. Model evaluation
8. New student grade prediction

## 7. Model Results

| Evaluation Metric | Result |
|---|---|
| Linear Regression MSE | 79.08 |
| Linear Regression R² | 0.6648 |
| Random Forest Accuracy | 36.42% |
| Classification Test Samples | 6,129 |

The Random Forest model has limited predictive accuracy and should be treated as an educational demonstration rather than a reliable academic assessment tool.

## 8. Generated Output Files

- `correlation_heatmap.png`
- `gender_distribution.png`
- `confusion_matrix.png`
- `actual_vs_predicted.png`
- `linear_regression_results.csv`
- `improved_random_forest_results.csv`

## 9. Installation and Execution

Install the required libraries:

```bash
python3 -m pip install pandas numpy matplotlib seaborn scikit-learn
```

Keep `student_performance.py` and `Expanded_data_with_more_features.csv` in the same folder.

Run the project:

```bash
python3 -u student_performance.py
```

The program displays evaluation results in the terminal and generates visualization files.

## 10. Limitations

- Grade classification accuracy is relatively low.
- Results depend on the available dataset.
- The model does not establish causal relationships.
- The regression model uses existing reading and writing scores, so it is not a forecast of performance before those scores are known.

## 11. Future Scope

- Improve feature engineering and model selection.
- Compare additional Machine Learning algorithms.
- Develop a user-friendly prediction interface.
- Evaluate models on additional datasets.

## 12. Conclusion

This project demonstrates how Machine Learning can be applied to student performance analysis. Linear Regression provides numerical score predictions, while Random Forest performs grade classification. The project also illustrates the importance of model evaluation and understanding predictive limitations.