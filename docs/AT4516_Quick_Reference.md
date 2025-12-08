# Anbai AT4516 Temperature Meter - Quick Reference

## Overview

The Anbai AT4516 is an 8-channel multi-channel temperature meter that supports various thermocouple types (K, T, J, N, E, S, R, B). This module provides Python control via RS-232 serial communication.

**Key Specifications:**
- **Channels**: 8 (expandable to 128 via RS-485)
- **Temperature Range**: -200°C to 1800°C (varies by thermocouple)
- **Resolution**: 0.1°C
- **Communication**: RS-232 (9600-115200 baud)
- **Protocol**: SCPI commands over serial

## Hardware Connection

### 1. Serial Connection
- **Interface**: RS-232 DB-9 connector (back panel)
- **Optional**: USB-Serial adapter (Applent ATN2 or generic USB-Serial)
- **Cable**: Non-null modem cable, max 2m length

### 2. Serial Port Settings
```
Baud Rate: 115200 (recommended)
Data Bits: 8
Stop Bits: 1
Parity: None
Terminator: \n (Line Feed)
```

### 3. Thermocouple Connection
- 16-pin terminal block (back panel)
- PIN 1,2: Channel 1 (+/-)
- PIN 3,4: Channel 2 (+/-)
- ... up to PIN 15,16: Channel 8 (+/-)

**Warning**: Ensure proper thermocouple polarity!

## Installation

### 1. Install pySerial
```bash
pip install pyserial
```

Or update requirements:
```bash
pip install -r requirements.txt
```

### 2. Find Your COM Port

**Windows:**
- Device Manager → Ports (COM & LPT)
- Look for "USB Serial Port (COMx)"

**Python:**
```python
from instruments.anbai import AT4516

# List all available COM ports
ports = AT4516.list_available_ports()
print(ports)  # ['COM3', 'COM4', 'COM5']
```

## Basic Usage

### Minimal Example
```python
from instruments.anbai import AT4516

# Create instance
temp_meter = AT4516(port='COM3', baudrate=115200)

# Connect
temp_meter.connect()

# Set thermocouple type
temp_meter.set_thermocouple_type('TC-K')

# Read all channels
temps = temp_meter.read_all_channels()
print(temps)  # [23.4, 23.5, None, None, None, None, None, None]

# Read specific channel
temp = temp_meter.read_channel(1)
print(f"Channel 1: {temp}°C")

# Disconnect
temp_meter.disconnect()
```

### Context Manager (Recommended)
```python
from instruments.anbai import AT4516

# Automatic connect/disconnect
with AT4516(port='COM3') as temp_meter:
    temp_meter.set_thermocouple_type('TC-K')
    temps = temp_meter.read_all_channels()
    print(temps)
# Automatically disconnected here
```

## Common Operations

### 1. Instrument Configuration

#### Set Thermocouple Type (All Channels)
```python
# Options: 'TC-T', 'TC-K', 'TC-J', 'TC-N', 'TC-E', 'TC-S', 'TC-R', 'TC-B'
temp_meter.set_thermocouple_type('TC-K')  # K-type
temp_meter.set_thermocouple_type('TC-T')  # T-type
```

#### Set Thermocouple Type (Specific Channel)
```python
temp_meter.set_channel_thermocouple(1, 'TC-K')  # Channel 1: K-type
temp_meter.set_channel_thermocouple(2, 'TC-T')  # Channel 2: T-type
```

#### Set Sampling Rate
```python
# Options: 'SLOW' (1s), 'MED' (0.5s), 'FAST' (0.1s)
temp_meter.set_sampling_rate('FAST')
```

#### Set Temperature Unit
```python
# Options: 'CEL' (Celsius), 'KEL' (Kelvin), 'FAH' (Fahrenheit)
temp_meter.set_temperature_unit('CEL')
```

### 2. Reading Temperatures

#### Read All Channels
```python
temps = temp_meter.read_all_channels()
# Returns: [23.4, 23.5, 23.3, None, None, None, None, None]
# None = disabled or error channel
```

#### Read Specific Channel
```python
temp = temp_meter.read_channel(1)  # Channel 1
if temp is not None:
    print(f"Temperature: {temp:.1f}°C")
else:
    print("Channel disabled or error")
```

#### Continuous Monitoring
```python
import time

with AT4516(port='COM3') as temp_meter:
    temp_meter.set_thermocouple_type('TC-K')
    temp_meter.start_measurement()

    while True:
        temps = temp_meter.read_all_channels()
        print(f"Temperatures: {temps}")
        time.sleep(1.0)
```

### 3. Channel Control

#### Enable/Disable Channels
```python
# Enable channel
temp_meter.enable_channel(1)

# Disable channel
temp_meter.disable_channel(8)
```

### 4. Limit Checking (Comparator)

#### Set Limits for All Channels
```python
# Set limits
temp_meter.set_low_limit(20.0)   # 20°C
temp_meter.set_high_limit(30.0)  # 30°C

# Enable comparator
temp_meter.enable_comparator()

# Enable beep on limit violation
temp_meter.enable_beep()
```

#### Set Limits for Specific Channel
```python
# Channel 1: 22-28°C range
temp_meter.set_channel_low_limit(1, 22.0)
temp_meter.set_channel_high_limit(1, 28.0)
```

### 5. System Control

#### Keypad Lock
```python
# Lock keypad (prevent front panel changes)
temp_meter.set_keypad_lock(True)

# Unlock keypad
temp_meter.set_keypad_lock(False)
```

#### Beep Control
```python
temp_meter.enable_beep()
temp_meter.disable_beep()

# Check status
is_beep_on = temp_meter.get_beep_status()
```

#### Start/Stop Measurement
```python
temp_meter.start_measurement()
temp_meter.stop_measurement()
```

### 6. Error Checking

```python
# Query instrument ID
idn = temp_meter.identify()
print(idn)  # 'AT4532,Rev.B5,SN123456,Applent Instruments'

# Check for errors
error = temp_meter.check_error()
print(error)  # 'no error' or error message
```

## Thermocouple Types & Ranges

| Type | Range (°C) | Accuracy (°C) | Common Use |
|------|------------|---------------|------------|
| **K** | -100 to 1350 | ±0.8 to ±1.2 | General purpose, most common |
| **T** | -150 to 400 | ±0.8 to ±1.0 | Low temperature, stable |
| **J** | -100 to 1200 | ±0.7 to ±1.0 | Reducing atmosphere |
| **N** | -100 to 1300 | ±0.9 to ±1.5 | High temperature stability |
| **E** | -100 to 850 | ±0.7 to ±0.9 | High sensitivity |
| **S** | 0 to 1750 | ±2.2 to ±4.5 | High temperature, platinum |
| **R** | 0 to 1750 | ±2.2 to ±4.5 | High temperature, platinum |
| **B** | 600 to 1800 | ±2.5 to ±5.5 | Very high temperature |

**Note**: Add ±0.5°C for cold junction compensation error.

## Troubleshooting

### Cannot Connect to Instrument

1. **Check COM port**:
   ```python
   ports = AT4516.list_available_ports()
   print(f"Available ports: {ports}")
   ```

2. **Check serial settings**:
   - Baud rate must match instrument setting (default: 115200)
   - Use Device Manager (Windows) to verify COM port

3. **Check USB-Serial driver**:
   - Install manufacturer's driver (e.g., FTDI, CH340)
   - Try different USB port

4. **Check cable**:
   - Use non-null modem cable
   - Cable length < 2m
   - Ensure pins 2 (RX), 3 (TX), 5 (GND) are connected

### Reading Returns None

- **Channel disabled**: Use `temp_meter.enable_channel(n)`
- **Thermocouple not connected**: Check physical connection
- **Wrong thermocouple type**: Set correct type with `set_thermocouple_type()`
- **Thermocouple polarity reversed**: Check +/- connections

### Timeout Errors

- Increase timeout: `AT4516(timeout=5.0)`
- Check serial connection is stable
- Reduce sampling rate: `set_sampling_rate('SLOW')`

### Permission Denied (Linux)

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Or change port permissions
sudo chmod 666 /dev/ttyUSB0
```

## Advanced Usage

### Multi-Channel Data Logging

```python
import time
from datetime import datetime
from instruments.anbai import AT4516

with AT4516(port='COM3') as meter:
    meter.set_thermocouple_type('TC-K')
    meter.set_sampling_rate('FAST')

    # Open log file
    with open('temperature_log.csv', 'w') as f:
        # Write header
        f.write('Timestamp,Ch1,Ch2,Ch3,Ch4,Ch5,Ch6,Ch7,Ch8\n')

        # Log data
        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            temps = meter.read_all_channels()

            # Convert None to empty string
            temp_strs = [str(t) if t is not None else '' for t in temps]

            # Write to file
            line = f"{timestamp},{','.join(temp_strs)}\n"
            f.write(line)
            f.flush()

            print(line.strip())
            time.sleep(1.0)
```

### Temperature Monitoring with Alerts

```python
from instruments.anbai import AT4516
import smtplib
from email.message import EmailMessage

def send_alert(channel, temp, limit):
    """Send email alert when temperature exceeds limit."""
    # Email configuration here
    pass

with AT4516(port='COM3') as meter:
    meter.set_thermocouple_type('TC-K')
    meter.set_high_limit(50.0)  # Alert threshold

    while True:
        temps = meter.read_all_channels()

        for i, temp in enumerate(temps, start=1):
            if temp and temp > 50.0:
                print(f"WARNING: Channel {i} over limit: {temp}°C")
                send_alert(i, temp, 50.0)

        time.sleep(5.0)
```

## API Reference

See `instruments/anbai/at4516.py` for complete API documentation.

### Main Methods

| Method | Description |
|--------|-------------|
| `connect()` | Establish serial connection |
| `disconnect()` | Close serial connection |
| `set_thermocouple_type(type)` | Set TC type for all channels |
| `read_all_channels()` | Read all 8 channels |
| `read_channel(n)` | Read specific channel (1-8) |
| `set_sampling_rate(rate)` | Set rate: SLOW/MED/FAST |
| `set_temperature_unit(unit)` | Set unit: CEL/KEL/FAH |
| `enable_channel(n)` | Enable channel |
| `disable_channel(n)` | Disable channel |
| `set_low_limit(limit)` | Set low limit (all channels) |
| `set_high_limit(limit)` | Set high limit (all channels) |
| `enable_comparator()` | Enable limit checking |
| `identify()` | Get instrument ID |
| `check_error()` | Get error status |

## Examples

See `examples/at4516_example.py` for complete working examples:
- Basic usage
- Continuous monitoring
- Limit checking with comparator
- Context manager usage
- COM port listing

## References

- **User Manual**: `instruments/anbai/AT45xx User's Guide RevB5.pdf`
- **Manufacturer**: Applent Instruments Inc. (www.applent.com)
- **Support**: tech@applent.com

## Project Integration

This module follows the project's design patterns:
- Similar structure to DSOX4034A and A34405A modules
- DEFAULT_RESOURCE class variable
- Context manager support (`__enter__`, `__exit__`)
- Comprehensive error handling
- Type hints for better IDE support

---

**Created**: 2025-12-05
**Author**: Claude Code
**Module**: `instruments.anbai.at4516`
