# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a temperature and pressure measurement board (溫度壓力量測板) project featuring BLE connectivity and multi-channel ADC data acquisition.

## Project Architecture

### Hardware Components

**MCU**: CH584M
- BLE (Bluetooth Low Energy) enabled microcontroller
- Interfaces with WebApp via BLE

**Temperature Measurement System**
- **NTC Thermistors**: 12 channels
- **ADC**: 24-bit multi-channel Sigma-Delta ADC
- **Interface**: Digital interface to MCU
- **Voltage Reference**: Precision voltage reference for temperature compensation
- **Power Filtering**: May be needed for ADC to ensure measurement accuracy

**Pressure Measurement System**
- **Channels**: 4 pressure sensors
- **ADC**: 4-channel ADC IC
- **Interface**: Connected to MCU

**Ambient Temperature**
- **Sensor**: Modular I2C temperature measurement IC
- **Interface**: I2C bus to MCU

### System Architecture

```
WebApp (BLE Client)
        ↕ [BLE]
    CH584M MCU
        ├─ [I2C] → Ambient Temperature Sensor
        ├─ [Digital Interface] → 24-bit ADC (12-ch NTC)
        │                         ↑
        │                    [Voltage Reference]
        │
        └─ [Digital Interface] → 4-ch ADC (Pressure)
```

### Communication Interfaces

- **BLE**: MCU ↔ WebApp communication
- **I2C**: MCU ↔ Ambient temperature sensor
- **SPI/Digital**: MCU ↔ Multi-channel ADCs
- **Analog**: Sensors → ADCs

## Project Language Notes

- Planning documents are in Traditional Chinese (繁體中文)
- File names may use Chinese characters
- The working directory path contains Chinese characters: `D:\Projects\實驗室\量測板`

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

### 📝 Documentation Update Protocol

**AUTOMATICALLY update BOTH files** after significant changes:

#### Update `docs/project/progress.md` when:
- ✅ Completing any implementation phase
- ✅ Changing project status or next steps
- ✅ Making important technical decisions (update "Technical Debt" or "Risks" sections)
- ✅ Identifying new tasks or changing priorities
- ✅ Updating risk mitigation strategies

**Update these sections**:
- "當前狀態" (Current Status)
- "下一步計畫" (Next Steps)
- "技術債務與未來改進" (Technical Debt)
- "風險與挑戰" (Risks)
- "更新日誌" (Update Log)

#### Update `docs/project/journal.md` when:
- ✅ Making ANY git commit (record hash and detailed description)
- ✅ Completing major work sessions (with timestamp)
- ✅ Making technical decisions (record rationale and alternatives considered)
- ✅ Encountering and solving problems (record issue and solution)
- ✅ Having important technical discussions
- ✅ Reaching project milestones

**Add entries with**:
- Timestamp (HH:MM format)
- Detailed description of work done
- Git commit hashes (after committing)
- Technical rationale for decisions
- Problem-solution pairs

#### Update `docs/project/todo.md` when:
- 💡 User mentions an idea or thought
- 🔬 Identifying research topics
- 🐛 Discovering bugs that aren't urgent
- ✨ Thinking of improvements
- ❓ Having questions to investigate later

**Management**:
- **Add freely** - Low friction, quick capture
- **Review periodically** - Help user prioritize during weekly reviews
- **Promote to progress.md** - When items become confirmed tasks
- **Archive** - Move completed/rejected items to Archive section

### 📊 Three-File System Explained

**The Information Flow**:
```
💭 Idea/Thought
    ↓
📝 todo.md (Capture)
    ↓ (Evaluate & Decide)
📋 progress.md (Plan)
    ↓ (Execute)
📖 journal.md (Record)
```

**File Characteristics**:

| File | Nature | Update Frequency | Lifetime | Structure |
|------|--------|------------------|----------|-----------|
| `todo.md` | Inbox | Very High (anytime) | Short (items move out) | Flexible |
| `progress.md` | Roadmap | Medium (phase changes) | Project duration | Structured |
| `journal.md` | Archive | High (after work) | Permanent | Chronological |

**When to use which file**:

- 💭 **Quick thought?** → `todo.md`
- 📋 **Confirmed task?** → `progress.md`
- ✅ **Work completed?** → `journal.md`

**Example flow**:
1. User: "我想研究看看是否可以加入語音提示功能"
   - → Add to `todo.md` under "Ideas"
2. After evaluation, user decides to do it
   - → Move to `progress.md` as "Phase X: Voice feedback feature"
3. After implementation and commit
   - → Record in `journal.md` with commit hash and details
   - → Mark as completed in `progress.md`
   - → Archive in `todo.md`

## Project Folder Structure

### Documentation Organization

```
./docs/
├── project/          # Project tracking and management
│   ├── progress.md   # Current status, roadmap, next steps
│   ├── journal.md    # Historical record, decisions, commits
│   └── todo.md       # Ideas inbox, research topics
│
└── research/         # Technical research reports
    └── *.md          # Comprehensive research documents
```

### Datasheets Organization

All component datasheets are organized by component type in the `Datasheets/` folder:

```
./Datasheets/
├── ADC/                    # ADC datasheets
│   ├── ADS1258/           # TI 16-ch 24-bit ADC (NTC measurement)
│   ├── ADS1220/           # TI 4-ch 24-bit ADC (pressure measurement)
│   ├── AD7124/            # ADI alternative ADC option
│   └── ...
│
├── MCU/                    # Microcontroller datasheets
│   └── CH584/             # WCH CH584M BLE MCU
│       ├── CH585/         # Related CH585 documents
│       └── CH585EVT/      # Evaluation board materials
│
├── Voltage-Reference/      # Precision voltage reference ICs
│   ├── MAX6350/           # ADI 5V reference (primary choice)
│   ├── REF5040/           # TI 4.096V reference (alternative)
│   └── ...
│
├── NTC/                    # NTC thermistor specifications
│   └── ...
│
└── LDO/                    # LDO voltage regulators
    └── ...
```

### Logseq Knowledge Graph

Research and technical knowledge organized as interconnected Logseq pages:

```
./logseq/
├── pages/                 # Knowledge base pages
│   ├── Lab Sensor Board.md        # Main project page
│   │
│   ├── Components/                 # Component pages
│   │   ├── ADS124S08.md           # NTC ADC (detailed specs, comparisons)
│   │   ├── ADS1220.md             # Pressure ADC
│   │   ├── CH584M.md              # BLE MCU
│   │   ├── MAX6350.md             # Voltage reference
│   │   └── TMP117.md              # I2C temperature sensor
│   │
│   ├── Concepts/                   # Technical concepts
│   │   ├── NTC Thermistor.md
│   │   ├── Steinhart-Hart Equation.md
│   │   ├── BLE EMI Management.md
│   │   ├── Power Budget Analysis.md
│   │   └── PCB Layout Strategy.md
│   │
│   └── Decisions/                  # Design decisions
│       ├── Component Selection Decision.md
│       └── ADC Selection Update.md
│
├── journals/              # Optional: Daily notes
│
└── logseq/                # Logseq configuration
    ├── config.edn         # Graph settings
    └── custom.css         # Optional: Custom styling
```

**Logseq Benefits**:
- **Bidirectional Links**: Connect related concepts (e.g., [[ADS124S08]] ↔ [[Power Budget]])
- **Graph View**: Visualize relationships between components and decisions
- **Properties**: Tag pages by type, status, manufacturer, etc.
- **Backlinks**: See all references to a component or concept
- **Hierarchical Structure**: Organize information naturally

**Usage**:
1. Open Logseq and add this folder as a graph
2. Start at "Lab Sensor Board" page for project overview
3. Follow links to explore components and concepts
4. Original markdown research reports remain in `docs/research/` for reference

### File Organization Guidelines

**When adding new documents:**

1. **Research Reports** → `docs/research/`
   - Comprehensive technical research
   - Component comparison studies
   - Reference design analysis
   - Application note summaries

2. **Datasheets** → `Datasheets/[ComponentType]/`
   - Create subfolder by component type if not exists
   - Common types: ADC, MCU, Voltage-Reference, NTC, LDO, Temperature-Sensor, Pressure-Sensor, Crystal, Connector, etc.
   - Keep manufacturer folder structure when useful (e.g., evaluation kits)

3. **Project Documents** → `docs/project/`
   - Only for progress.md, journal.md, todo.md
   - Do not add other files here

4. **Naming Conventions**:
   - Use descriptive names for research reports
   - Keep original datasheet filenames when possible
   - Use component part numbers in folder names for clarity

## Git Repository

**Remote Repository**: `git@github.com:Cleanstation/Lab_Sensor-Board.git`

### 🔄 Update Workflow Example

After completing a phase or significant work:

1. **Code changes** → `git commit`
   ```bash
   git add .
   git commit -m "descriptive commit message"
   ```

2. **Get commit hash** → `git log -1 --format=%H`
   ```bash
   git log -1 --format='%H %s'
   ```

3. **Update journal.md**:
   ```markdown
   ### HH:MM - Phase X Complete

   **工作內容 / Work Done**:
   - Detailed description of changes
   - Implementation details

   **技術決策 / Technical Decisions**:
   - Decision rationale
   - Alternatives considered

   **Git 提交 / Git Commits**:
   - `abc1234...` - "commit message"
     - Detailed explanation of what was changed
     - Why this approach was chosen

   **遇到的問題 / Problems Encountered**:
   - Issues and their solutions
   ```

4. **Update progress.md**:
   ```markdown
   ### Phase X (✅ Completed - YYYY-MM-DD)
   - [x] Task description
   - Update status from "pending" to "completed"
   - Move relevant items from "下一步計畫" to "已完成"
   - Add entry to "更新日誌"
   ```

5. **Archive in todo.md**:
   ```markdown
   ### YYYY-MM-DD
   - ✅ Completed task description
   ```

6. **Push to remote**:
   ```bash
   git push origin main
   ```

### Commit Message Guidelines

- **Format**: Use clear, descriptive messages in English or Chinese
- **Structure**:
  ```
  Short summary (50 chars or less)

  Detailed description if needed:
  - What was changed
  - Why it was changed
  - Any important considerations
  ```
- **Examples**:
  - `feat: Add ADS124S08 ADC driver implementation`
  - `docs: Update component selection to ADS124S08`
  - `fix: Correct SPI timing for CH584M compatibility`
  - `refactor: Simplify NTC thermistor calculation`
  - `test: Add unit tests for Steinhart-Hart equation`

## Current Project Status

The project is in the planning/specification phase. The main reference document is `量測板規劃.txt` which outlines the hardware components and communication interfaces to be used.

## Development Considerations

When code is added to this repository, it will likely involve:
- Embedded firmware for ADC interfacing (SPI communication)
- I2C sensor communication for ambient temperature
- Data acquisition and processing for NTC thermistors and pressure sensors
- Power measurement and isolation circuitry control
- 24-bit multi-channel ADC handling

## File Encoding

Files in this repository may use UTF-8 encoding to support Chinese characters.
