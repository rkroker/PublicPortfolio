# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm

# Load dataset (you can replace this with your own dataset)
# For example, we'll use a dataset of housing prices
url = 'https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv'
data = pd.read_csv(url)

# Display first few rows of the dataset
print("First five rows of the dataset:")
print(data.head())

# Check for missing values
print("\nMissing values in each column:")
print(data.isnull().sum())

# Basic statistics of the dataset
print("\nBasic statistical description:")
print(data.describe())

# Data Cleaning: Checking for outliers
# We'll use box plots to visualize potential outliers
plt.figure(figsize=(20, 10))
for i, column in enumerate(data.columns):
    plt.subplot(4, 4, i + 1)
    sns.boxplot(y=data[column])
    plt.title(column)
plt.tight_layout()
plt.show()

# Exploratory Data Analysis (EDA)
# Correlation matrix to see how features are correlated with each other
plt.figure(figsize=(12, 8))
corr_matrix = data.corr()
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm')
plt.title("Correlation Matrix")
plt.show()

# Visualize the relationship between two highly correlated features
sns.jointplot(x='RM', y='MEDV', data=data, kind='reg')
plt.title("Relationship between RM (Number of rooms) and MEDV (Median value of homes)")
plt.show()

# Data Preprocessing: Feature Selection
# Select features that are most correlated with the target variable 'MEDV'
features = ['RM', 'LSTAT', 'PTRATIO']
X = data[features]
y = data['MEDV']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build a Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print("\nModel Evaluation:")
print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")

# Visualizing the actual vs predicted values
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, edgecolor='k', alpha=0.7)
plt.plot([min(y_test), max(y_test)], [min(y_pred), max(y_pred)], color='red', linewidth=2)
plt.title('Actual vs Predicted Values')
plt.xlabel('Actual MEDV')
plt.ylabel('Predicted MEDV')
plt.show()

# Advanced Analysis: Checking the statistical significance of each feature
X_with_const = sm.add_constant(X_train)
model_sm = sm.OLS(y_train, X_with_const).fit()
print("\nStatistical Summary:")
print(model_sm.summary())
