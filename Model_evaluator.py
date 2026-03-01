import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    explained_variance_score,
    classification_report,
    confusion_matrix
)

# ==========================================================
# LOAD DATASET
# ==========================================================

df = pd.read_csv("smart_dustbin_2025_complete_dataset.csv")

# Align weekday format with server
df["day_of_week"] = pd.to_datetime(df["timestamp"]).dt.weekday

# ==========================================================
# FEATURES & TARGETS
# ==========================================================

X = df.drop(columns=["timestamp",
                     "next_fill_rate_wet",
                     "next_fill_rate_dry"])

y_wet = df["next_fill_rate_wet"]
y_dry = df["next_fill_rate_dry"]

# ==========================================================
# TRAIN TEST SPLIT
# ==========================================================

X_train, X_test, y_wet_train, y_wet_test = train_test_split(
    X, y_wet, test_size=0.2, random_state=42
)

_, _, y_dry_train, y_dry_test = train_test_split(
    X, y_dry, test_size=0.2, random_state=42
)

# ==========================================================
# LOAD MODELS
# ==========================================================

wet_model = joblib.load("wet_model.pkl")
dry_model = joblib.load("dry_model.pkl")

# Ensure feature order matches training
X_train = X_train[wet_model.feature_names_in_]
X_test = X_test[wet_model.feature_names_in_]

# ==========================================================
# PREDICTIONS
# ==========================================================

wet_pred_train = wet_model.predict(X_train)
wet_pred_test = wet_model.predict(X_test)

dry_pred_train = dry_model.predict(X_train)
dry_pred_test = dry_model.predict(X_test)

# ==========================================================
# REGRESSION METRICS FUNCTION
# ==========================================================

def evaluate_regression(y_true, y_pred, name):

    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mape = np.mean(
    np.abs((y_true - y_pred) / np.maximum(y_true, 0.01))
) * 100
    evs = explained_variance_score(y_true, y_pred)

    print(f"\n===== {name} Evaluation =====")
    print("R2 Score:", round(r2, 4))
    print("MAE:", round(mae, 4))
    print("MSE:", round(mse, 4))
    print("RMSE:", round(rmse, 4))
    print("MAPE:", round(mape, 2), "%")
    print("Explained Variance:", round(evs, 4))

# ==========================================================
# EVALUATION RESULTS
# ==========================================================

print("\n=========== TRAIN PERFORMANCE ===========")
evaluate_regression(y_wet_train, wet_pred_train, "Wet Train")
evaluate_regression(y_dry_train, dry_pred_train, "Dry Train")

print("\n=========== TEST PERFORMANCE ===========")
evaluate_regression(y_wet_test, wet_pred_test, "Wet Test")
evaluate_regression(y_dry_test, dry_pred_test, "Dry Test")

# ==========================================================
# ACTUAL vs PREDICTED GRAPH
# ==========================================================

plt.figure()
plt.scatter(y_wet_test, wet_pred_test)
plt.xlabel("Actual Wet")
plt.ylabel("Predicted Wet")
plt.title("Wet Actual vs Predicted")
plt.show()

plt.figure()
plt.scatter(y_dry_test, dry_pred_test)
plt.xlabel("Actual Dry")
plt.ylabel("Predicted Dry")
plt.title("Dry Actual vs Predicted")
plt.show()

# ==========================================================
# RESIDUAL DISTRIBUTION
# ==========================================================

wet_residuals = y_wet_test - wet_pred_test
dry_residuals = y_dry_test - dry_pred_test

plt.figure()
plt.hist(wet_residuals, bins=30)
plt.title("Wet Residual Distribution")
plt.xlabel("Residual")
plt.ylabel("Frequency")
plt.show()

plt.figure()
plt.hist(dry_residuals, bins=30)
plt.title("Dry Residual Distribution")
plt.xlabel("Residual")
plt.ylabel("Frequency")
plt.show()

# ==========================================================
# CLASSIFICATION STYLE EVALUATION
# ==========================================================

def categorize(rate):
    if rate < 1:
        return "Low"
    elif rate < 2:
        return "Medium"
    else:
        return "High"

y_wet_true_cat = y_wet_test.apply(categorize)
y_wet_pred_cat = pd.Series(wet_pred_test).apply(categorize)

print("\n===== Wet Classification Report =====")
print(classification_report(y_wet_true_cat, y_wet_pred_cat))
print("Confusion Matrix:")
print(confusion_matrix(y_wet_true_cat, y_wet_pred_cat))

# ==========================================================
# FEATURE IMPORTANCE (If Available)
# ==========================================================

try:
    importances = wet_model.named_steps["model"].feature_importances_
    features = wet_model.feature_names_in_

    plt.figure()
    plt.barh(features, importances)
    plt.title("Wet Model Feature Importance")
    plt.show()

except:
    print("\nFeature importance not available for this model type.")