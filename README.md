# Laboratory Instrument Control

A Python project for controlling lab instruments via USB or Ethernet using VISA.

## Supported Instruments

- **Keysight DSOX4034A** - InfiniiVision 4000 X-Series Oscilloscope

## Installation

1. Activate virtual environment: `.venv\Scriptsctivate` (Windows)
2. Install dependencies: `pip install -r requirements.txt`

## Quick Start

```python
from instruments.keysight import DSOX4034A

# Connect to oscilloscope
with DSOX4034A("TCPIP0::192.168.1.100::INSTR") as scope:
    print(scope.identify())
    scope.autoscale()
    
    # Acquire waveform
    time, voltage = scope.get_waveform(channel=1)
    
    # Make measurements
    vpp = scope.measure_vpp(1)
    print(f"Vpp: {vpp} V")
```

## Examples

See `examples/dsox4034a_example.py` for detailed examples.

## Documentation

- CLAUDE.md - Development guidelines
- docs/project/ - Project tracking
- Instrument modules have comprehensive docstrings

## References

- [PyVISA Documentation](https://pyvisa.readthedocs.io/)
- [DSOX4034A Programmer Guide](https://www.keysight.com/us/en/assets/9018-06976/programming-guides/9018-06976.pdf)
