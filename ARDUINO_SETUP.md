# Arduino Integration Setup Guide

## Overview
Your Flask Health Monitor app now supports real-time Arduino communication to automatically collect vital signs from connected sensors.

## Required Libraries

### Python Libraries (Flask App)
```bash
pip install pyserial
```

### Arduino Libraries (Upload to Arduino)
- **PulseSensorPlayground** (if using pulse sensor) - Download from Arduino Library Manager
- **DHT** (if using DHT11/DHT22 temperature sensor) - Optional

## Hardware Setup

### Required Sensors
1. **Temperature Sensor**: LM35 or DHT11/DHT22
2. **Heart Rate Sensor**: Pulse sensor module or KY-039
3. **Blood Pressure Sensor**: BMP085/BMP180 module or analog BP sensors

### Arduino Pin Configuration
```
Temperature Sensor  → A0
Heart Rate Sensor   → A1
Systolic BP Sensor  → A2
Diastolic BP Sensor → A3
GND                 → GND
5V                  → 5V
```

### Schematic
```
Arduino Uno
├── A0 → LM35 (Temperature)
├── A1 → Pulse Sensor (Heart Rate)
├── A2 → BP Sensor Systolic
├── A3 → BP Sensor Diastolic
└── USB → Computer (Communication Port)
```

## Installation Steps

### Step 1: Upload Arduino Code
1. Open Arduino IDE
2. Copy the code from `ARDUINO_CODE.ino`
3. Select **Tools → Board → Arduino Uno** (or your board)
4. Select **Tools → Port → COM3** (check your port)
5. Click **Upload**
6. Open **Tools → Serial Monitor** and verify:
   ```
   ARDUINO_READY
   TEMP:36.5,HR:72,SYSBP:120,DIABP:80
   ```

### Step 2: Find Your Arduino Port
Run this Python command in your terminal:
```python
import serial.tools.list_ports
ports = [port.device for port in serial.tools.list_ports.comports()]
print(ports)
```
You'll see output like: `['COM3', 'COM4']`

### Step 3: Update Arduino Port in Flask App
Edit `app.py` and change this line:
```python
ARDUINO_PORT = "COM3"  # Change to your Arduino's COM port
```

### Step 4: Restart Flask App
```bash
python app.py
```

## API Endpoints (New)

### 1. List Available Ports
```
GET /arduino/ports
Response: {"ports": ["COM3", "COM4"], "current": "COM3"}
```

### 2. Connect to Arduino
```
POST /arduino/connect
Body: {"port": "COM3"}
Response: {"success": true, "message": "Connected to COM3"}
```

### 3. Read Current Data from Arduino
```
GET /arduino/read
Response: {"success": true, "data": {"TEMP": 37.2, "HR": 75, "SYSBP": 120, "DIABP": 80}}
```

### 4. Auto-Read and Save to Database
```
POST /arduino/auto-read
Response: {"success": true, "status": "Normal", "disease": "Healthy", "alerts": "Vitals Normal"}
```

### 5. Check Arduino Connection Status
```
GET /arduino/status
Response: {"connected": true, "port": "COM3"}
```

## Usage in Dashboard

### Option A: Manual Button (Add to dashboard.html)
```html
<button id="readArduino">Read from Arduino</button>

<script>
document.getElementById('readArduino').addEventListener('click', function() {
    fetch('/arduino/auto-read', {method: 'POST'})
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                alert('Status: ' + data.status);
            } else {
                alert('Error: ' + data.error);
            }
        });
});
</script>
```

### Option B: Auto-Read Every 30 Seconds
```html
<script>
setInterval(function() {
    fetch('/arduino/auto-read', {method: 'POST'})
        .then(res => res.json())
        .then(data => console.log(data));
}, 30000);
</script>
```

## Troubleshooting

### Problem: "No data from Arduino"
- Check USB cable connection
- Verify correct COM port
- Open Arduino Serial Monitor to test

### Problem: "Port already in use"
- Close Serial Monitor or other apps using the port
- Restart Arduino IDE
- Reconnect USB cable

### Problem: Incorrect sensor readings
- Calibrate each sensor individually
- Adjust the `map()` function values in Arduino code
- Add offset values if needed

### Problem: "Failed to connect"
```python
# Test connection manually:
import serial
ser = serial.Serial('COM3', 9600, timeout=1)
print(ser.readline())
```

## Sensor Calibration

### Temperature (LM35)
- Formula: Temperature = (ADC * 5 / 1024) * 100
- Test: Place in warm water (40°C) to verify

### Heart Rate
- Normal: 60-100 BPM
- Test after exercise (100-120 BPM expected)

### Blood Pressure
- Normal: Systolic 90-120, Diastolic 60-80
- Adjust `map()` range based on sensor specifications

## Next Steps

1. ✅ Upload Arduino code
2. ✅ Identify COM port
3. ✅ Update `ARDUINO_PORT` in app.py
4. ✅ Restart Flask app
5. ✅ Test `/arduino/status` endpoint
6. ✅ Add UI buttons to dashboard.html
7. ✅ calibrate sensors for accuracy

## Support Files
- `ARDUINO_CODE.ino` - Arduino sketch
- `app.py` - Updated Flask app with Arduino support
