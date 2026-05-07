// ============================================
// HEALTH MONITOR - ARDUINO CODE
// Reads Temperature, Heart Rate, and Blood Pressure sensors
// ============================================

// Define Sensor Pins
#define TEMP_SENSOR A0      // Temperature sensor (LM35 or DHT11)
#define HR_SENSOR A1        // Heart rate sensor
#define BP_SYS_SENSOR A2    // Systolic BP sensor
#define BP_DIA_SENSOR A3    // Diastolic BP sensor

// Variables for sensor data
float temperature = 0;
int heart_rate = 0;
int systolic_bp = 0;
int diastolic_bp = 0;

void setup() {
  Serial.begin(9600);  // Start serial communication at 9600 baud
  delay(2000);         // Wait for Arduino to initialize
  Serial.println("ARDUINO_READY");
}

void loop() {
  // Read sensors
  readSensors();
  
  // Send data in format: TEMP:37.5,HR:75,SYSBP:120,DIABP:80
  String data = "TEMP:" + String(temperature) + 
                ",HR:" + String(heart_rate) + 
                ",SYSBP:" + String(systolic_bp) + 
                ",DIABP:" + String(diastolic_bp);
  
  Serial.println(data);
  
  // Check for acknowledgement from Flask app
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command.indexOf("ACK_SAVED") >= 0) {
      Serial.println("DATA_SAVED_OK");
    }
  }
  
  delay(5000);  // Read every 5 seconds
}

void readSensors() {
  // ===== TEMPERATURE SENSOR (LM35) =====
  // LM35: 10mV per degree Celsius
  int rawTemp = analogRead(TEMP_SENSOR);
  temperature = (rawTemp * 5.0 / 1023.0) * 100;  // Convert to Celsius
  
  // ===== HEART RATE SENSOR =====
  // Using pulse sensor countdigital pulses
  heart_rate = readHeartRate();
  
  // ===== BLOOD PRESSURE SENSORS =====
  // These require analog sensors or BMP085/BMP180 module
  int rawSysBP = analogRead(BP_SYS_SENSOR);
  int rawDiaBP = analogRead(BP_DIA_SENSOR);
  
  // Convert ADC values to BP readings (calibrate based on your sensors)
  systolic_bp = map(rawSysBP, 0, 1023, 80, 180);    // Map to 80-180 range
  diastolic_bp = map(rawDiaBP, 0, 1023, 50, 120);   // Map to 50-120 range
}

int readHeartRate() {
  // Simple pulse detection
  // For better accuracy, use a dedicated pulse sensor library
  int pulses = 0;
  unsigned long start = millis();
  
  while (millis() - start < 6000) {  // Count pulses for 6 seconds
    if (analogRead(HR_SENSOR) > 512) {
      delay(50);
      while (analogRead(HR_SENSOR) > 512) {
        delay(10);
      }
      pulses++;
      delay(50);
    }
  }
  
  return (int)(pulses * 10);  // Convert to BPM (pulses per minute)
}

// ============================================
// ALTERNATIVE: Using Pulse Sensor Library
// Uncomment below if using Adafruit or similar
// ============================================
/*
#include <PulseSensorPlayground.h>

PulseSensorPlayground pulseSensor;

void setup() {
  Serial.begin(9600);
  pulseSensor.analogInput(HR_SENSOR);
  pulseSensor.begin();
}

void loop() {
  heart_rate = pulseSensor.getBeatsPerMinute();
  // ... rest of code
}
*/
