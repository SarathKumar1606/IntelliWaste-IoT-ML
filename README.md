# ♻️ IntelliWaste-IoT-ML  
### AI-Powered Smart Waste Management System  

> Swacch Bharat: An IoT Initiative  
> Developed by Sarathkumar R & Team | IST, CEG  

---

## 📌 Project Overview

IntelliWaste-IoT-ML is a cloud-connected AI-powered smart waste segregation and predictive waste management system.

This system integrates:

- Embedded IoT hardware (ESP32)
- Real-time ultrasonic sensing
- AI-based waste level prediction (Machine Learning)
- Holiday-aware dynamic modeling
- Cloud-hosted ML backend
- Telegram alert integration
- OLED live dashboard display

The system not only segregates waste into wet and dry categories but also predicts when each bin will reach critical capacity and proactively schedules pickup.

---

## 🚀 Key Features

### 🔹 Intelligent Waste Segregation
- Moisture-based classification (Wet / Dry)
- Servo-controlled mechanical sorting flap

### 🔹 AI-Based Predictive Fill Modeling
- Dual regression models (Wet & Dry bins)
- Time-aware and holiday-aware prediction
- Dynamic pickup scheduling
- Threshold-based alerting

### 🔹 Cloud ML Backend
- Flask-based prediction server
- Hosted on Railway cloud
- REST API architecture
- Real-time JSON communication

### 🔹 Holiday-Aware Intelligence
- Uses Indian national & religious holiday engine
- Dynamic holiday factor modeling
- Festival-aware prediction scaling

### 🔹 Smart Alerts
- Telegram bot integration
- Pickup alert notifications
- Real-time bin statistics
- Holiday greetings display

### 🔹 Live OLED Dashboard
Displays:
- Current date & time (cloud synced)
- Day of week
- Wet bin % + ETA
- Dry bin % + ETA
- Pickup alerts
- Holiday greetings
- Project branding footer

---

## 🧠 Machine Learning Details

### Model Type
- Supervised Regression
- Separate models for Wet & Dry bins

### Input Features
- Hour of day
- Day of week
- Weekend indicator
- Holiday factor
- Holiday flag
- Weather condition
- Current bin levels
- Average fill rate
- Previous day level

### Performance Metrics

#### Wet Model (Test Data)
- R² Score: ~0.95
- RMSE: ~0.16
- MAE: ~0.13

#### Dry Model (Test Data)
- R² Score: ~0.94
- RMSE: ~0.14
- MAE: ~0.11

Residuals are normally distributed and centered around zero, indicating stable and unbiased predictions.

---

## 🏗️ Hardware Architecture

### Components Used

- ESP32 DevKit V1
- 3 × HC-SR04 Ultrasonic Sensors
- Capacitive Soil Moisture Sensor
- SG90 Servo Motor
- 0.96” SSD1306 OLED Display
- Active Buzzer
- External 5V Power Supply
- Breadboard & Jumper Wires
- Voltage Divider for Ultrasonic Echo pins

---

## 🌐 System Architecture

ESP32 → Sends bin levels → Cloud ML Server  
Cloud ML Server → Predicts fill rate & ETA  
Cloud → Sends structured JSON response  
ESP32 → Displays ETA & Alerts → Sends Telegram notification  

---

## 📡 API Endpoint

POST `/predict`

### Request JSON Example

```json
{
  "wet_level": 72.5,
  "dry_level": 65.0,
  "avg_fill_rate_last_3h": 1.5,
  "previous_day_same_time_level": 50,
  "weather_condition": "normal"
}
