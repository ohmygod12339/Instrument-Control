# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Instrument Control project for controlling laboratory instruments via USB or Ethernet using VISA and other communication protocols. The project provides individual Python modules for each instrument as reusable components.

## Project Architecture

### System Components

**Communication Interfaces**:
- **USB**: Direct USB connection to instruments
- **Ethernet/LAN**: Network-based instrument control
- **VISA**: Standard instrument control protocol (PyVISA)

**Supported Instruments**:
- Keysight DSOX4034A Oscilloscope (InfiniiVision 4000 X-Series)
- (Additional instruments to be added)

### System Architecture

```
User Python Script
        ↓
    Instrument Modules (instruments/)
        ↓
    PyVISA / Communication Layer
        ↓ [USB/Ethernet]
    Laboratory Instruments
```

### Project Structure

```
./
├── PAPAPIN_*_*.py           # Main project scripts (see naming convention below)
├── GENERAL_*_*.py           # General utility scripts
│
├── instruments/              # Individual instrument modules
│   ├── __init__.py          # Package initialization
│   ├── base_logger.py       # Base class for data loggers (IMPORTANT)
│   ├── keysight/            # Keysight instruments
│   │   ├── __init__.py
│   │   └── dsox4034a.py     # DSOX4034A oscilloscope class
│   ├── agilent/             # Agilent instruments
│   │   ├── __init__.py
│   │   └── a34405a.py       # 34405A DMM class
│   └── digilent/            # Digilent instruments
│       ├── __init__.py
│       └── analog_discovery2.py  # AD2 class
│
├── examples/                # Example usage scripts
│   └── *.py
│
├── results/                 # Output Excel files
│
├── docs/                    # Documentation
│   ├── project/             # Project tracking and management
│   │   ├── progress.md      # Current status, roadmap, next steps
│   │   ├── journal.md       # Historical record, decisions, commits
│   │   ├── todo.md          # Ideas inbox, research topics
│   │   └── development-guide.md  # Coding conventions and standards (IMPORTANT)
│   │
│   └── research/            # Technical research reports
│       └── *.md             # Comprehensive research documents
│
├── .venv/                   # Python virtual environment
├── requirements.txt         # Python dependencies
├── CLAUDE.md               # This file
└── README.md               # Project README
```

## Key Development Conventions

**IMPORTANT: Read `docs/project/development-guide.md` for complete details.**

### Python File Naming Convention

Main scripts follow: `<Project>_<instruments>_<measurements>.py`

Examples:
- `PAPAPIN_dsox4034a_vrms.py` - Oscilloscope Vrms measurement
- `PAPAPIN_dsox4034a-ad2_vrms-temp.py` - Oscilloscope + AD2, Vrms + temperature
- `GENERAL_all_find-instruments.py` - Utility script

### BaseDataLogger Template

All data loggers MUST inherit from `instruments.base_logger.BaseDataLogger` for:
- Precise timing compensation (not just `time.sleep()`)
- Buffered Excel output
- Elapsed time tracking in milliseconds
- Dual-file system (main + FINAL for viewing)

Required methods to implement:
- `setup_instrument()` - Connect and configure
- `read_measurement()` - Read one value, return None on error
- `cleanup_instrument()` - Disconnect
- `get_headers()` - Return Excel column headers

### Standard Excel Columns

Every data logger MUST include:
1. **Timestamp** - Format: `HH:MM:SS:mmm`
2. **Elapsed Time (ms)** - Milliseconds since test start

### Instrument Module Design

Each instrument class should have:
- `DEFAULT_RESOURCE` class variable with lab's default address
- Optional `resource_string` parameter (None = use default)
- Context manager support (`__enter__`, `__exit__`)

## Project Language Notes

- Code and comments are in English
- Documentation may be in Traditional Chinese (繁體中文) or English
- The working directory path contains Chinese characters: `D:\Projects\實驗室\Instrument-Control`

## Project Tracking System

**ALWAYS read these files at the start of each session**:
1. `docs/project/progress.md` - Current status, formal plans, structured roadmap (forward-looking)
2. `docs/project/journal.md` - Historical record, decisions, commits (backward-looking)
3. `docs/project/todo.md` - Ideas inbox, research topics, quick notes (flexible collection)

This gives you complete context about:
- Current project status and active tasks
- Completed work and historical timeline
- Technical decisions and their rationale
- Commit history with hashes/tags
- Known risks and challenges
- User's ideas and research interests

### Documentation Update Protocol

**AUTOMATICALLY update BOTH files** after significant changes:

#### Update `docs/project/progress.md` when:
- Completing any implementation phase
- Changing project status or next steps
- Making important technical decisions
- Identifying new tasks or changing priorities
- Updating risk mitigation strategies

**Update these sections**:
- "當前狀態" (Current Status)
- "下一步計畫" (Next Steps)
- "技術債務與未來改進" (Technical Debt)
- "風險與挑戰" (Risks)
- "更新日誌" (Update Log)

#### Update `docs/project/journal.md` when:
- Making ANY git commit (record hash and detailed description)
- Completing major work sessions (with timestamp)
- Making technical decisions (record rationale and alternatives considered)
- Encountering and solving problems (record issue and solution)
- Having important technical discussions
- Reaching project milestones

**Add entries with**:
- Timestamp (HH:MM format)
- Detailed description of work done
- Git commit hashes (after committing)
- Technical rationale for decisions
- Problem-solution pairs

#### Update `docs/project/todo.md` when:
- User mentions an idea or thought
- Identifying research topics
- Discovering bugs that aren't urgent
- Thinking of improvements
- Having questions to investigate later

## Development Considerations

### Instrument Module Design Pattern

Each instrument should be implemented as a Python class with:
- Clear initialization (connection setup)
- Read methods (get parameters, measurements)
- Write methods (set parameters, configurations)
- Error handling
- Connection management (open/close)
- Documentation of SCPI commands used

Example structure:
```python
class InstrumentName:
    def __init__(self, resource_string):
        """Initialize connection to instrument"""

    def connect(self):
        """Establish connection"""

    def disconnect(self):
        """Close connection"""

    def read_parameter(self):
        """Read a specific parameter"""

    def write_parameter(self, value):
        """Set a specific parameter"""

    def get_measurement(self):
        """Get measurement data"""
```

### Communication Protocols

- **PyVISA**: Primary library for VISA communication
- **PyVISA-py**: Pure Python backend (no VISA libraries required)
- **SCPI Commands**: Standard commands for programmable instruments

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Include docstrings for all classes and public methods
- Add inline comments for complex operations
- Use meaningful variable and function names

## Current Project Status

The project is in the initial development phase. Currently implementing the DSOX4034A oscilloscope control module.

## File Encoding

Files in this repository use UTF-8 encoding to support Chinese characters.
