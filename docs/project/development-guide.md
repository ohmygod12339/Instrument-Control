# Development Guide / 開發指南

This document describes the coding conventions, design patterns, and standards used in this project.

本文件描述本專案使用的編碼規範、設計模式和標準。

---

## 1. Python File Naming Convention / Python 檔案命名規則

### Main Script Files (Root Directory)

All main script files in the root directory follow this naming pattern:

```
<Project>_<instruments>_<measurements>.py
```

**Format:**
- **Project**: Project name or `GENERAL` for utility scripts
- **Instruments**: Instruments used, separated by `-` (lowercase)
- **Measurements**: What is being measured/recorded, separated by `-`

**Examples:**

| Filename | Description |
|----------|-------------|
| `PAPABIN_dsox4034a_vrms.py` | PAPABIN project, oscilloscope, Vrms measurement |
| `PAPABIN_dsox4034a_vrms-fast.py` | PAPABIN project, oscilloscope, fast Vrms measurement |
| `PAPABIN_dsox4034a-a34405a_vrms-temp.py` | PAPABIN project, oscilloscope + DMM, Vrms + temperature |
| `PAPABIN_dsox4034a-ad2_vrms-temp.py` | PAPABIN project, oscilloscope + AD2, Vrms + temperature |
| `GENERAL_all_find-instruments.py` | General utility to find all instruments |
| `GENERAL_dsox4034a_read-scope-settings.py` | General utility to read oscilloscope settings |

### Instrument Module Files

Instrument modules are organized by manufacturer in `instruments/`:

```
instruments/
├── __init__.py
├── base_logger.py           # Base class for data loggers
├── keysight/
│   ├── __init__.py
│   └── dsox4034a.py         # Module name = model number (lowercase)
├── agilent/
│   ├── __init__.py
│   └── a34405a.py
└── digilent/
    ├── __init__.py
    └── analog_discovery2.py
```

---

## 2. Data Logger Template / 資料記錄器模板

### BaseDataLogger Class

All data loggers should inherit from `instruments.base_logger.BaseDataLogger` to ensure consistent behavior.

**Location:** `instruments/base_logger.py`

### Key Features

1. **Precise Timing Compensation** - Not affected by processing time
2. **Buffered Excel Output** - Reduces disk I/O for performance
3. **Elapsed Time Tracking** - Milliseconds from test start
4. **Dual-File System** - Main file + FINAL file for viewing

### Required Methods to Implement

```python
from instruments.base_logger import BaseDataLogger

class MyLogger(BaseDataLogger):
    def setup_instrument(self):
        """Connect and configure instruments."""
        pass

    def read_measurement(self):
        """Read one measurement. Return None on error."""
        pass

    def cleanup_instrument(self):
        """Disconnect instruments."""
        pass

    def get_headers(self):
        """Return Excel column headers."""
        return ["Timestamp", "Value", "Elapsed Time (ms)", "Elapsed Time (hr)"]
```

### Optional Methods to Override

```python
    def format_measurement(self, timestamp_str, elapsed_ms, measurement):
        """Format measurement into Excel row."""
        return [timestamp_str, measurement, elapsed_ms]

    def format_display(self, timestamp_str, elapsed_ms, measurement):
        """Format measurement for console display."""
        return f"{timestamp_str} | {measurement} | {elapsed_ms:.1f} ms"
```

### Configuration Parameters

```python
BaseDataLogger(
    results_dir="results",        # Output directory
    save_interval=50,             # Save to disk every N measurements
    measurement_interval=0.1,     # Seconds between measurements (100ms)
    final_copy_interval=300       # Seconds between FINAL updates (5min)
)
```

### Usage Example

```python
class MyLogger(BaseDataLogger):
    def __init__(self, **kwargs):
        kwargs.setdefault('measurement_interval', 0.2)  # 200ms
        kwargs.setdefault('save_interval', 50)
        super().__init__(**kwargs)
        self.instrument = None

    def setup_instrument(self):
        self.instrument = MyInstrument()
        self.instrument.connect()

    def read_measurement(self):
        try:
            return self.instrument.read()
        except:
            return None

    def cleanup_instrument(self):
        if self.instrument:
            self.instrument.disconnect()

    def get_headers(self):
        return ["Timestamp", "Value", "Elapsed Time (ms)", "Elapsed Time (hr)"]

# Run the logger
logger = MyLogger()
logger.start()  # Handles everything automatically
```

---

## 3. Timing and Elapsed Time / 時間記錄規則

### Standard Output Columns

**Every data logger MUST include these columns:**

| Column | Format | Description |
|--------|--------|-------------|
| Timestamp | `HH:MM:SS:mmm` | Absolute time of measurement |
| Elapsed Time (ms) | Float | Milliseconds since test start |
| Elapsed Time (hr) | Float | Hours since test start (for plotting) |

**Elapsed Time (hr) Calculation:**
```python
elapsed_hr = elapsed_ms / 3_600_000  # ms to hours
```

This column is used by `GENERAL_all_plot-results.py` for plotting with a more readable x-axis scale.

### Precise Timing Implementation

The BaseDataLogger uses timing compensation to ensure accurate measurement intervals:

```python
next_measurement_time = time.time()

while running:
    # Take measurement
    now = datetime.now()
    elapsed_ms = (now - start_time).total_seconds() * 1000

    # ... process measurement ...

    # Precise timing compensation
    next_measurement_time += measurement_interval
    sleep_time = next_measurement_time - time.time()

    if sleep_time > 0:
        time.sleep(sleep_time)
    else:
        # Running behind schedule - reset timing
        if sleep_time < -measurement_interval:
            print(f"Warning: Running {-sleep_time:.3f}s behind")
            next_measurement_time = time.time()
```

**Important:** Do NOT use simple `time.sleep(interval)` as it doesn't account for processing time.

### Excel Output Format

```
results/
├── Result_YYYYMMDD_HHMMSS_Real-Time-Result.xlsx       # Main file (being written)
└── Result_YYYYMMDD_HHMMSS_Real-Time-Result_FINAL.xlsx # Copy for viewing
```

---

## 4. Instrument Module Design / 儀器模組設計規則

### Class Structure

Each instrument module should follow this pattern:

```python
class InstrumentName:
    """
    Instrument description and specifications.

    Example:
        >>> inst = InstrumentName()
        >>> inst.connect()
        >>> value = inst.measure_something()
        >>> inst.disconnect()
    """

    # Default resource string for lab instrument
    DEFAULT_RESOURCE = "TCPIP::192.168.2.60::INSTR"

    def __init__(self, resource_string: Optional[str] = None, timeout: int = 5000):
        """Initialize with optional custom resource string."""
        self.resource_string = resource_string or self.DEFAULT_RESOURCE
        self.timeout = timeout
        self.instrument = None

    def connect(self) -> None:
        """Establish connection to instrument."""
        pass

    def disconnect(self) -> None:
        """Close connection to instrument."""
        pass

    def write(self, command: str) -> None:
        """Write SCPI command."""
        pass

    def query(self, command: str) -> str:
        """Query instrument and return response."""
        pass

    # Measurement methods
    def measure_xxx(self) -> float:
        """Measure specific parameter."""
        pass

    # Configuration methods
    def set_xxx(self, value) -> None:
        """Set specific parameter."""
        pass

    def get_xxx(self) -> Any:
        """Get specific parameter."""
        pass

    # Context manager support
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
```

### Default Resource Strings

Each instrument class should define a `DEFAULT_RESOURCE` class variable with the lab's default instrument address:

```python
# USB instruments
DEFAULT_RESOURCE = "USB0::2391::1560::TW47310002::0::INSTR"

# Ethernet instruments
DEFAULT_RESOURCE = "TCPIP::192.168.2.60::INSTR"
```

This allows users to connect without specifying the resource string:

```python
# Use default
scope = DSOX4034A()
scope.connect()

# Or specify custom
scope = DSOX4034A("TCPIP::10.0.0.100::INSTR")
scope.connect()
```

### Error Handling

- Use `try-except` blocks in measurement methods
- Return `None` on measurement errors (don't raise exceptions)
- Print warning messages for non-critical errors
- Raise exceptions for connection failures

### Documentation

- Include docstrings for all public methods
- Document SCPI commands used in comments
- Provide usage examples in class docstring

---

## 5. Current Lab Instruments / 目前實驗室儀器

| Instrument | Model | Default Resource |
|------------|-------|------------------|
| Oscilloscope | Keysight DSOX4034A | `TCPIP::192.168.2.60::INSTR` |
| DMM | Agilent 34405A | `USB0::2391::1560::TW47310002::0::INSTR` |
| DAQ | Digilent Analog Discovery 2 | First available device |

---

## 6. Code Style / 程式碼風格

- Follow PEP 8 style guidelines
- Use type hints for function parameters and returns
- Use docstrings for all classes and public methods
- Use meaningful variable names
- Comments in English, documentation can be bilingual

---

## 7. Quick Start for New Developers / 新開發者快速入門

### Creating a New Data Logger

1. **Inherit from BaseDataLogger**
2. **Implement 4 required methods**
3. **Set default measurement_interval and save_interval**
4. **Name file following convention: `<Project>_<instruments>_<measurements>.py`**

### Template

```python
import sys
import signal
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])

from instruments.base_logger import BaseDataLogger
from instruments.keysight import DSOX4034A

class MyLogger(BaseDataLogger):
    def __init__(self, resource=None, **kwargs):
        kwargs.setdefault('measurement_interval', 0.1)  # 100ms
        kwargs.setdefault('save_interval', 50)
        super().__init__(**kwargs)
        self.resource = resource
        self.instrument = None

    def setup_instrument(self):
        self.instrument = DSOX4034A(self.resource)
        self.instrument.connect()
        # Configure instrument...

    def read_measurement(self):
        try:
            return self.instrument.measure_vrms(1)
        except:
            return None

    def cleanup_instrument(self):
        if self.instrument:
            self.instrument.disconnect()

    def get_headers(self):
        return ["Timestamp", "Vrms (V)", "Elapsed Time (ms)", "Elapsed Time (hr)"]

def main():
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    logger = MyLogger()
    logger.start()

if __name__ == "__main__":
    main()
```

---

## Update History / 更新歷史

### 2025-11-18
- Initial version created
- Documented naming conventions, BaseDataLogger template, and instrument module rules
