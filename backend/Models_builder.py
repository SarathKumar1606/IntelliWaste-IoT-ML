import pandas as pd
import joblib

from sklearn.model_selection import GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

# ----------------------------------
# LOAD DATA
# ----------------------------------
df = pd.read_csv("smart_dustbin_2025_complete_dataset.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

df["day_of_week"] = df["timestamp"].dt.dayofweek

# ----------------------------------
# TARGETS
# ----------------------------------
target_wet = "next_fill_rate_wet"
target_dry = "next_fill_rate_dry"

X = df.drop(columns=["timestamp", target_wet, target_dry])

y_wet = df[target_wet]
y_dry = df[target_dry]

categorical_cols = ["weather_condition"]
numerical_cols = [col for col in X.columns if col not in categorical_cols]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numerical_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
])

def train_model(y, model_name):

    model = XGBRegressor(objective="reg:squarederror")

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    param_grid = {
        "model__n_estimators": [200],
        "model__max_depth": [4, 6],
        "model__learning_rate": [0.05, 0.1]
    }

    grid = GridSearchCV(
        pipeline,
        param_grid,
        cv=5,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )

    grid.fit(X, y)

    best_model = grid.best_estimator_
    joblib.dump(best_model, model_name)

    print(f"{model_name} saved.")

train_model(y_wet, "wet_model.pkl")
train_model(y_dry, "dry_model.pkl")