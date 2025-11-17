# Performance Improvements - Vrms Logger

## Problem Identified

The initial implementation was **very slow** (~2 seconds per measurement instead of 100ms) due to:

1. **Saving Excel file after EVERY measurement** - This was the main bottleneck
2. **No timing compensation** - Simple `sleep(0.1)` didn't account for measurement/processing time
3. **Oscilloscope not explicitly set to RUN mode**

## Solutions Implemented

### 1. Data Buffering (MAJOR IMPROVEMENT)

**Before:**
```python
def log_data(self, timestamp_str: str, vrms: float):
    # Add data to worksheet
    self.worksheet.cell(...)

    # Save to file EVERY TIME (SLOW!)
    self.workbook.save(self.main_file_path)
```

**After:**
```python
def buffer_data(self, timestamp_str: str, vrms: float):
    # Add to buffer
    self.data_buffer.append((timestamp_str, vrms))

    # Only save when buffer reaches threshold (e.g., 50 measurements)
    if len(self.data_buffer) >= self.save_interval:
        self.flush_buffer()
```

**Result:**
- Saves to disk every 50 measurements instead of every measurement
- Reduces disk I/O by 98%
- Should achieve near-100ms measurement intervals

### 2. Precise Timing Compensation

**Before:**
```python
while True:
    measure()
    time.sleep(0.1)  # Always sleeps 0.1s regardless of how long measure() took
```

**After:**
```python
target_interval = 0.1  # 100ms
next_measurement_time = time.time()

while True:
    measure()

    # Calculate next measurement time
    next_measurement_time += target_interval

    # Compensate for processing time
    sleep_time = next_measurement_time - time.time()
    if sleep_time > 0:
        time.sleep(sleep_time)
```

**Result:**
- Measurements occur at precise 100ms intervals
- Compensates for SCPI query time and processing time
- Warns if running behind schedule

### 3. Oscilloscope Configuration

**Added:**
```python
def connect(self):
    self.scope.connect()

    # Ensure Channel 1 is on
    self.scope.channel_on(1)

    # Set to continuous RUN mode
    self.scope.run()
```

**Result:**
- Oscilloscope continuously updates measurements
- No need to trigger for each measurement
- Faster SCPI query responses

## Usage

```bash
# Default: saves every 50 measurements
python vrms_logger.py "USB0::0x0957::0x17A6::MY12345678::INSTR"

# Custom save interval (e.g., every 100 measurements)
python vrms_logger.py "USB0::0x0957::0x17A6::MY12345678::INSTR" 100
```

## Expected Performance

- **Measurement interval:** ~100ms (10 Hz)
- **Disk write frequency:** Every 50 measurements (5 seconds with default)
- **FINAL file update:** Every 5 minutes
- **Data safety:** Buffer flushed on Ctrl+C or error

## Trade-offs

| Aspect | Before | After |
|--------|--------|-------|
| Speed | ~2 seconds/measurement | ~100ms/measurement |
| Disk I/O | Every measurement | Every 50 measurements |
| Data loss risk | Minimal (immediate save) | Small (max 50 measurements if crash) |
| Memory usage | Minimal | Small buffer (~2KB per 50 measurements) |

## Additional Features

- **Configurable save interval** - Adjust based on your needs
- **Warning system** - Alerts if running behind schedule
- **Automatic buffer flush** - On exit, error, or 5-minute FINAL update
- **Measurement counter** - Shows total measurements on exit
