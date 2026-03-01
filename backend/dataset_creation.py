import pandas as pd
import numpy as np
from datetime import datetime
import random

# -------------------------------------
# 1. Generate Hourly Data for 2025
# -------------------------------------

start = datetime(2025, 1, 1)
end = datetime(2025, 12, 31, 23)

timestamps = pd.date_range(start, end, freq="H")

df = pd.DataFrame({"timestamp": timestamps})

df["hour_of_day"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.day_name()
df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)
df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")

# -------------------------------------
# 2. Holiday Dictionary
# -------------------------------------

holiday_dict = {
    "2025-01-14": 0.2,
    "2025-01-26": 0.3,
    "2025-02-26": 0.2,
    "2025-03-14": 0.6,
    "2025-03-30": 0.2,
    "2025-03-31": 0.6,
    "2025-04-06": 0.3,
    "2025-04-10": 0.2,
    "2025-04-14": 0.3,
    "2025-05-12": 0.2,
    "2025-06-07": 0.6,
    "2025-07-06": 0.2,
    "2025-08-09": 0.2,
    "2025-08-16": 0.2,
    "2025-10-02": 0.3,
    "2025-10-03": 0.6,
    "2025-10-04": 0.4,
    "2025-10-20": 0.7,
    "2025-10-22": 0.2,
    "2025-12-25": 0.4
}

df["holiday_factor"] = df["date"].map(holiday_dict).fillna(0)
df["is_holiday"] = (df["holiday_factor"] > 0).astype(int)

# -------------------------------------
# 3. Weather Simulation
# -------------------------------------

weather_conditions = ["normal", "rainy", "hot"]

df["weather_condition"] = np.random.choice(
    weather_conditions,
    size=len(df),
    p=[0.6, 0.25, 0.15]
)

def weather_bonus(weather):
    if weather == "rainy":
        return 0.3
    elif weather == "hot":
        return 0.1
    return 0

# -------------------------------------
# 4. Simulate Wet & Dry Separately
# -------------------------------------

wet_level = 20
dry_level = 20

wet_levels = []
dry_levels = []

wet_rates = []
dry_rates = []

for i in range(len(df)):

    hour = df.loc[i, "hour_of_day"]
    weekend = df.loc[i, "is_weekend"]
    holiday = df.loc[i, "holiday_factor"]
    weather = df.loc[i, "weather_condition"]

    # Base rate logic
    if 0 <= hour <= 6:
        base_rate = 0.5
    elif weekend:
        base_rate = 2.5
    else:
        base_rate = 1.5

    # Wet rate
    wet_rate = (
        base_rate
        + holiday
        + weather_bonus(weather)
        + np.random.normal(0, 0.2)
    )

    # Dry rate slightly lower and less affected by weather
    dry_rate = (
        base_rate * 0.8
        + holiday * 0.7
        + np.random.normal(0, 0.15)
    )

    wet_level += wet_rate
    dry_level += dry_rate

    # Reset if full
    if wet_level >= 100:
        wet_level = random.randint(5, 20)

    if dry_level >= 100:
        dry_level = random.randint(5, 20)

    wet_levels.append(round(wet_level, 2))
    dry_levels.append(round(dry_level, 2))

    wet_rates.append(round(wet_rate, 2))
    dry_rates.append(round(dry_rate, 2))

df["wet_level"] = wet_levels
df["dry_level"] = dry_levels

df["next_fill_rate_wet"] = wet_rates
df["next_fill_rate_dry"] = dry_rates

# -------------------------------------
# 5. Advanced ML Features
# -------------------------------------

df["avg_fill_rate_last_3h"] = (
    df["next_fill_rate_wet"]
    .rolling(3)
    .mean()
    .fillna(0)
)

df["previous_day_same_time_level"] = (
    df["wet_level"]
    .shift(24)
    .fillna(0)
)

df.drop(columns=["date"], inplace=True)

# -------------------------------------
# 6. Save Dataset
# -------------------------------------

df.to_csv("smart_dustbin_2025_complete_dataset.csv", index=False)

print("✅ Dual Fill Rate Dataset Created Successfully")
print("Total rows:", len(df))