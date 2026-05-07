# Arduino Integration - Quick Start (Tamil)

## என்ன செய்தேன்?

உங்கள் Flask App-ல் Arduino communication functionality சேர்த்துவிட்டேன்.

### 1. **New Features**
- ✅ Arduino சரியாக connect பண்ணுதல்
- ✅ Temperature, Heart Rate, BP sensors கிட்ட data வாங்குதல்
- ✅ automatically database-ல save பண்ணुதल்
- ✅ Real-time vitals reading

### 2. **Required Installation**
```bash
pip install pyserial
```

### 3. **Arduino Setup**

#### Hardware connections:
```
Arduino Pin A0 ← Temperature Sensor (LM35)
Arduino Pin A1 ← Heart Rate Sensor
Arduino Pin A2 ← BP Systolic
Arduino Pin A3 ← BP Diastolic
Arduino GND    ← All Sensors GND
Arduino 5V     ← All Sensors VCC
```

#### Arduino Code Upload:
1. `ARDUINO_CODE.ino` file open பண்ணு
2. Arduino IDE-ல copy paste பண்ணు
3. Upload பண்ணு

### 4. **Flask App Update**

**app.py-ல unnai PORT update панну:**
```python
ARDUINO_PORT = "COM3"  # உங்கட Arduino COM port
ARDUINO_BAUD = 9600
```

COM port search பанну:
```python
import serial.tools.list_ports
ports = [p.device for p in serial.tools.list_ports.comports()]
print(ports)
```

### 5. **New API Endpoints**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/arduino/ports` | GET | Available ports list |
| `/arduino/connect` | POST | Arduino-ula connect pannuдалу |
| `/arduino/read` | GET | Current vitals data vaanguдалу |
| `/arduino/auto-read` | POST | Auto-read and DB save |
| `/arduino/status` | GET | Connection status |

### 6. **Dashboard-ल Button Add Pannu** (Optional)

```html
<div class="col-md-4">
    <button class="btn btn-info" id="readArduino">
        <span class="glyphicon glyphicon-refresh"></span> Arduino से पढ़ें
    </button>
</div>

<script>
document.getElementById('readArduino').addEventListener('click', function() {
    fetch('/arduino/auto-read', {method: 'POST'})
        .then(r => r.json())
        .then(d => {
            if(d.success) {
                alert('✅ Status: ' + d.status + '\n📊 Disease: ' + d.disease);
            } else {
                alert('❌ Error: ' + d.error);
            }
        });
});
</script>
```

### 7. **Testing**

Terminal-ल chey:
```bash
python app.py
```

Web browser-ल open pannu:
```
http://localhost:5000/arduino/status
```

Response varunathu:
```json
{
  "connected": true,
  "port": "COM3"
}
```

### 8. **Troubleshooting**

| Problem | Solution |
|---------|----------|
| "No data from Arduino" | USB cable check, COM port verify |
| "Port already in use" | Serial Monitor close pannu |
| Wrong readings | Sensors calibrate pannu |
| Connection error | Arduino IDE-lla serial monitor test pannu |

### 9. **Next**

1. Arduino code upload pannu
2. COM port identify pannu (COM3, COM4, etc)
3. `ARDUINO_PORT` update pannu
4. Flask restart pannu
5. `/arduino/status` test pannu
6. Dashboard button add pannu (optional)
7. Sensor calibration pannu

### Files Created:
- ✅ `ARDUINO_CODE.ino` - Arduino sketch
- ✅ `ARDUINO_SETUP.md` - Detailed guide
- ✅ `app.py` - Updated with Arduino support

**Ready to go! Arduino ka vitals ab automatically read-aega! 🎉**
