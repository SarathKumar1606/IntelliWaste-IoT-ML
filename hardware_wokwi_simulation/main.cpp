#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ================= WIFI =================
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// ================= ML SERVER =================
#define SERVER_URL "https://smart-bin-ml-backend-production.up.railway.app/predict"

// ================= TELEGRAM =================
#define BOT_TOKEN "YOUR_BOT_TOKEN"
#define CHAT_ID   "YOUR_CHAT_ID"

WiFiClientSecure telegramClient;
UniversalTelegramBot bot(BOT_TOKEN, telegramClient);

// ================= OLED =================
Adafruit_SSD1306 display(128, 64, &Wire, -1);

// ================= PINS =================
#define SERVO_PIN 15
#define BUZZER_PIN 4
#define MOISTURE_PIN 34
#define TRIG1 12
#define ECHO1 13
#define TRIG2 26
#define ECHO2 27
#define TRIG3 32
#define ECHO3 33

Servo servo1;

// ================= GLOBAL VARIABLES =================
float wetPercent = 0;
float dryPercent = 0;
float wetHoursRemaining = 0;
float dryHoursRemaining = 0;

bool pickupImmediate = false;
bool alertSent = false;

String selectedBin = "";
String currentDate = "";
String currentTime = "";
String dayName = "";
String holidayName = "";
bool isHoliday = false;

unsigned long lastRequest = 0;
unsigned long screenTimer = 0;
int screenIndex = 0;

// ================= ULTRASONIC =================
long readDistance(int trig, int echo) {
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long duration = pulseIn(echo, HIGH, 30000);
  return duration * 0.034 / 2;
}

// ================= TELEGRAM FULL STATUS =================
void sendFullStatusToTelegram(String title) {

  String msg = title + "\n\n";
  msg += "Date: " + dayName + " " + currentDate + "\n";
  msg += "Time: " + currentTime + "\n\n";
  msg += "Wet: " + String(wetPercent,1) + "% | ETA: " + String(wetHoursRemaining,1) + "h\n";
  msg += "Dry: " + String(dryPercent,1) + "% | ETA: " + String(dryHoursRemaining,1) + "h\n";
  msg += "Next Bin to collect : " + selectedBin + " bin\n"; 

  if (isHoliday) {
    msg += "\nHoliday: " + holidayName;
  }

  bot.sendMessage(CHAT_ID, msg, "");

  Serial.println("Telegram Sent:");
  Serial.println(msg);
}

// ================= ML REQUEST =================
void requestPrediction() {

  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  WiFiClientSecure secureClient;
  secureClient.setInsecure();

  http.begin(secureClient, SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> req;
  req["wet_level"] = wetPercent;
  req["dry_level"] = dryPercent;
  req["avg_fill_rate_last_3h"] = 1.5;
  req["previous_day_same_time_level"] = 50;
  req["weather_condition"] = "normal";

  String body;
  serializeJson(req, body);

  int httpCode = http.POST(body);

  if (httpCode == 200) {

    String response = http.getString();
    StaticJsonDocument<1024> doc;
    if (!deserializeJson(doc, response)) {

      wetHoursRemaining = doc["wet_hours_remaining"] | 0.0;
      dryHoursRemaining = doc["dry_hours_remaining"] | 0.0;
      pickupImmediate = doc["pickup_required_immediately"] | false;
      selectedBin = doc["selected_bin_for_pickup"] | "";

      currentDate = doc["current_date"] | "";
      currentTime = doc["current_time"] | "";
      dayName = doc["day_name"] | "";

      isHoliday = doc["is_holiday_today"] | false;
      holidayName = doc["holiday_name"] | "";

      if (pickupImmediate && !alertSent) {
        sendFullStatusToTelegram("SMART BIN PICKUP ALERT");
        alertSent = true;
        pickupImmediate=false;
      }

      if (!pickupImmediate) alertSent = false;
    }
  }

  http.end();
}

// ================= DISPLAY MAIN =================
void drawMainScreen() {

  display.clearDisplay();
  display.setCursor(0,0);

  display.println("AI SMART WASTE SYSTEM");
  display.println(dayName + " " + currentDate);
  display.println(currentTime);

  display.print("Wet:");
  display.print(wetPercent,0);
  display.print("% ETA:");
  display.print(wetHoursRemaining,1);
  display.println("h");

  display.print("Dry:");
  display.print(dryPercent,0);
  display.print("% ETA:");
  display.print(dryHoursRemaining,1);
  display.println("h");

if (pickupImmediate) {
  display.println("!! PICKUP ALERT !!");
  digitalWrite(BUZZER_PIN, HIGH);
} else {
  if (isHoliday) {
    display.println("");
    display.println("Happy " + holidayName + "!");
  } else {
    display.println("HAPPY HOLI!!");
  }
  digitalWrite(BUZZER_PIN, LOW);
}

  display.display();
}

// ================= DISPLAY FOOTER =================
void drawFooterScreen() {

  display.clearDisplay();
  display.setCursor(0,5);

  display.println("Swacch Bharat: Clean India, Green India!");
  display.println("An IOT initiative by:");
  display.println("Sarathkumar R and");
  display.println("Divya, IST, CEG.");

  if (isHoliday) {
    display.println("");
    display.println("Happy " + holidayName + "!");
  } else {
    display.println("HAPPY HOLI!!");
  }

  display.display();
}

// ================= ANALYZING SCREEN =================
void showAnalyzingScreen(String type, int moisture) {

  display.clearDisplay();
  display.setCursor(0,10);

  display.println("Analyzing...");
  display.println("");
  display.print("Type: ");
  display.println(type);
  display.print("Moisture: ");
  display.print(moisture);
  display.println("%");

  display.display();
}

// ================= SETUP =================
void setup() {

  Serial.begin(115200);

  Wire.begin(21,22);
  display.begin(SSD1306_SWITCHCAPVCC,0x3C);
  display.setTextColor(WHITE);

  pinMode(BUZZER_PIN,OUTPUT);
  pinMode(TRIG1,OUTPUT); pinMode(ECHO1,INPUT);
  pinMode(TRIG2,OUTPUT); pinMode(ECHO2,INPUT);
  pinMode(TRIG3,OUTPUT); pinMode(ECHO3,INPUT);

  servo1.attach(SERVO_PIN);
  servo1.write(90);

  WiFi.begin(ssid,password);
  while (WiFi.status()!=WL_CONNECTED) delay(500);

  telegramClient.setInsecure();

  bot.sendMessage(CHAT_ID,"AI Smart Bin Cloud System Started","");
}

// ================= LOOP =================
void loop() {

  long wetDistance = readDistance(TRIG2,ECHO2);
  long dryDistance = readDistance(TRIG3,ECHO3);
  long objectDistance = readDistance(TRIG1,ECHO1);

  wetPercent = constrain(map(wetDistance,30,5,0,100),0,100);
  dryPercent = constrain(map(dryDistance,30,5,0,100),0,100);

  if (millis() - lastRequest > 30000) {
    requestPrediction();
    lastRequest = millis();
  }

  // Waste detection
  if (objectDistance > 2 && objectDistance < 15) {

    int soil = analogRead(MOISTURE_PIN);
    int moisture = map(soil,0,4095,0,100);

    String type;

    if (moisture >= 55) {
      type = "WET";
      servo1.write(180);
    } else {
      type = "DRY";
      servo1.write(0);
    }

    Serial.println("Waste Detected -> " + type);

    showAnalyzingScreen(type, moisture);

    delay(4000);  // show analyzing screen

    servo1.write(90);
  }

  // Screen rotation
  if (millis() - screenTimer > 5000) {
    screenIndex = (screenIndex + 1) % 2;
    screenTimer = millis();
  }

  if (screenIndex == 0)
    drawMainScreen();
  else
    drawFooterScreen();

  delay(300);
}