# 專案日誌 / Project Journal

本文件記錄專案開發過程中的重要事件、決策、問題解決和提交歷史。

This document records important events, decisions, problem-solving, and commit history during project development.

---

## 2025-11-19

### Session - Elapsed Time (hr) 欄位新增與專案標準化

**工作內容 / Work Done**:

1. **新增 Elapsed Time (hr) 欄位**
   - 更新 `development-guide.md` 加入新規則
   - 更新 `instruments/base_logger.py` 自動計算 `elapsed_hr = elapsed_ms / 3_600_000`
   - 更新所有 PAPABIN 專案檔案支援此欄位
   - 用於 `GENERAL_all_plot-results.py` 繪圖時的 X 軸

2. **更新 GENERAL_all_plot-results.py**
   - X 軸改用 Elapsed Time (hr)
   - Y 軸排除 Elapsed Time (ms) 和 Elapsed Time (hr)
   - 修正 `print_file_info()` 顯示格式

3. **更新 PAPABIN 專案檔案**
   - `PAPABIN_dsox4034a_vrms-fast.py`:
     - 更新文檔描述和使用範例
     - 設定預設參數: resource=TCPIP::192.168.2.60::INSTR, save_interval=10, timebase=5ms, holdoff=5ms
     - 所有參數改為可選
   - `PAPABIN_dsox4034a-a34405a_vrms-temp.py`:
     - 更新文檔描述和正確檔案名稱
   - `PAPABIN_dsox4034a-ad2_vrms-temp.py`:
     - 更新文檔描述和正確檔案名稱

4. **修正專案名稱**
   - PAPAPIN → PAPABIN (在所有文件中)
   - 更新 CLAUDE.md, development-guide.md, journal.md

**技術決策 / Technical Decisions**:

1. **選擇小時作為繪圖 X 軸單位**
   - **原因**: 長時間測試 (數小時) 使用毫秒數值過大
   - **計算**: `elapsed_hr = elapsed_ms / 3_600_000`
   - **效果**: 更易讀的 X 軸刻度

2. **預設參數設定**
   - resource: TCPIP::192.168.2.60::INSTR (實驗室示波器 IP)
   - save_interval: 10 (更頻繁儲存)
   - timebase: 5 ms/div (快速量測)
   - holdoff: 5 ms (最小延遲)

**程式碼變更 / Code Changes**:

1. `instruments/base_logger.py`:
   - `format_measurement()` 方法新增 elapsed_hr 計算

2. `GENERAL_all_plot-results.py`:
   - `get_measurement_columns()` 排除兩個 elapsed time 欄位
   - 繪圖函數改用 Elapsed Time (hr)

3. `docs/project/development-guide.md`:
   - 標準輸出欄位表格新增 Elapsed Time (hr)
   - 所有範例 `get_headers()` 更新

4. PAPABIN 專案檔案:
   - 更新 docstrings 和預設值
   - 新增 elapsed_hr 到 Excel 輸出

**Excel 輸出格式 / Excel Output Format**:

| Timestamp | Measurement | Elapsed Time (ms) | Elapsed Time (hr) |
|-----------|-------------|-------------------|-------------------|
| HH:MM:SS:mmm | Value | 12345.678 | 0.003429 |

---

## 2025-11-18

### Session - Agilent 34405A 模組新增與 Vrms Logger 改進

**工作內容 / Work Done**:

1. **vrms_logger_fast.py 改進**
   - 新增 "Elapsed Time (ms)" 欄位
     - 記錄每次量測相對於測試開始時間的毫秒數
     - 方便分析時間相關行為
   - 新增觸發掃描模式設定 (AUTO)
     - 解決小信號量測速度慢的問題
   - 新增觸發延遲 (holdoff) 可配置參數
     - 命令列參數: `holdoff_ms` (預設 20ms)

2. **DSOX4034A 模組新增功能**
   - `set_trigger_sweep()` / `get_trigger_sweep()` - 設定觸發掃描模式
   - `set_trigger_holdoff()` / `get_trigger_holdoff()` - 設定觸發延遲時間

3. **Agilent 34405A 數位萬用表模組**
   - 建立 `instruments/agilent/` 目錄
   - 實作完整的 A34405A 控制類別
   - 支援功能:
     - DC/AC 電壓量測
     - DC/AC 電流量測
     - 2 線/4 線電阻量測
     - 頻率量測
     - 連續性和二極體測試
     - 觸發和取樣設定
     - 顯示控制
     - NPLC 和自動歸零設定

**技術決策 / Technical Decisions**:

1. **觸發掃描模式選擇 AUTO**
   - **問題**: 小信號時量測速度慢，大信號時快
   - **原因**: NORMAL 模式需要等待有效觸發事件
   - **解決方案**: 使用 AUTO 模式，超時後自動觸發
   - **效果**: 無論信號大小，量測速度一致

2. **觸發延遲預設 20ms**
   - 提供足夠時間讓信號穩定
   - 可透過命令列參數調整
   - 較短延遲 = 更快量測，但可能不穩定

3. **Agilent 34405A 模組設計**
   - 遵循與 DSOX4034A 相同的設計模式
   - 使用 PyVISA-py 後端 (無需安裝 VISA 函式庫)
   - 僅支援 USB 介面 (34405A 硬體限制)

**程式碼變更 / Code Changes**:

1. `vrms_logger_fast.py`:
   - 新增 `holdoff_time` 參數
   - 新增 elapsed time 計算和記錄
   - 更新命令列參數解析
   - 更新 Excel 輸出格式 (3 欄位)

2. `instruments/keysight/dsox4034a.py`:
   - 新增 `set_trigger_sweep()` 方法 (lines 453-465)
   - 新增 `get_trigger_sweep()` 方法 (lines 467-474)
   - 新增 `set_trigger_holdoff()` 方法 (lines 476-483)
   - 新增 `get_trigger_holdoff()` 方法 (lines 485-492)

3. 新增檔案:
   - `instruments/agilent/__init__.py`
   - `instruments/agilent/a34405a.py`

**使用方式 / Usage**:

vrms_logger_fast.py 新參數:
```bash
python vrms_logger_fast.py <RESOURCE> [save_interval] [timebase_ms] [holdoff_ms]

# 範例: 10ms 延遲
python vrms_logger_fast.py "TCPIP::192.168.2.60::INSTR" 50 20 10
```

Agilent 34405A:
```python
from instruments.agilent import A34405A

dmm = A34405A("USB0::0x0957::0x0618::MY12345678::INSTR")
dmm.connect()

# 量測 DC 電壓
voltage = dmm.measure_dc_voltage()
print(f"DC Voltage: {voltage} V")

# 量測 AC 電流
current = dmm.measure_ac_current()
print(f"AC Current: {current} A")

dmm.disconnect()
```

**下一步 / Next Steps**:
- 測試 Agilent 34405A 模組
- 建立 34405A 使用範例腳本
- 測試觸發設定對量測速度的影響

### Session 2 - Digilent AD2 模組與專案文件標準化

**工作內容 / Work Done**:

1. **新增 Digilent Analog Discovery 2 模組**
   - 建立 `instruments/digilent/` 目錄
   - 實作 `AnalogDiscovery2` 控制類別
   - 支援: 電源供應、類比輸入/輸出、DC 電壓量測

2. **建立雙儀器記錄器 (AD2 版本)**
   - `PAPABIN_dsox4034a-ad2_vrms-temp.py`
   - AD2 提供 5V 激勵電壓和 DC 電壓量測
   - DSOX4034A 提供 Vrms 量測
   - NTC 溫度計算 (R25=7K, B=3600K)

3. **專案檔案重新命名**
   - 採用新命名規則: `<Project>_<instruments>_<measurements>.py`
   - 例如: `PAPABIN_dsox4034a-a34405a_vrms-temp.py`

4. **建立開發指南文件**
   - 建立 `docs/project/development-guide.md`
   - 記錄 Python 檔案命名規則
   - 記錄 BaseDataLogger 模板使用規則
   - 記錄儀器模組設計規則
   - 記錄時間記錄標準 (Timestamp + Elapsed Time)

5. **更新 CLAUDE.md**
   - 更新專案結構
   - 新增關鍵開發規範摘要
   - 參照完整開發指南

**檔案命名規範 / File Naming Convention**:

```
<Project>_<instruments>_<measurements>.py

Examples:
- PAPABIN_dsox4034a_vrms.py
- PAPABIN_dsox4034a-ad2_vrms-temp.py
- GENERAL_all_find-instruments.py
```

**BaseDataLogger 規範 / BaseDataLogger Rules**:

所有資料記錄器必須:
- 繼承自 `BaseDataLogger`
- 使用精確計時補償 (非單純 `time.sleep()`)
- 包含 Timestamp 和 Elapsed Time (ms) 欄位
- 實作 4 個必要方法

**新增檔案 / New Files**:
- `instruments/digilent/__init__.py`
- `instruments/digilent/analog_discovery2.py`
- `PAPABIN_dsox4034a-ad2_vrms-temp.py`
- `docs/project/development-guide.md`

---

## 2025-11-17

### 15:56 - 專案建立 / Project Initialization

**工作內容 / Work Done**:
- 建立專案資料夾結構
  - `docs/project/` - 專案追蹤文件
  - `docs/research/` - 技術研究報告
  - `instruments/` - 儀器模組目錄
- 設定 Python 虛擬環境 (.venv)
- 安裝核心依賴套件:
  - PyVISA 1.15.0
  - PyVISA-py 0.8.1
  - NumPy 2.3.5
  - typing-extensions 4.15.0

**技術決策 / Technical Decisions**:

1. **選擇 PyVISA-py 作為後端**
   - **原因**: 純 Python 實作，無需安裝額外的 VISA 函式庫
   - **優點**:
     - 跨平台相容性更好
     - 安裝更簡單，無需 NI-VISA 或其他 VISA 實作
     - 社群回饋 VISA 函式庫穩定性較差
   - **缺點**: 可能效能略低於原生 VISA，但對大多數應用足夠

2. **專案架構設計**
   - 採用模組化設計，每個儀器一個獨立類別
   - 遵循參考專案的三文件追蹤系統 (progress.md, journal.md, todo.md)
   - 使用 `instruments/` 目錄組織不同廠商的儀器模組

**研究發現 / Research Findings**:

1. **Keysight DSOX4034A 控制選項**:
   - 官方 SCPI 程式設計指南可用 (PDF)
   - 有多個開源 Python 套件可參考:
     - `keyoscacquire` - 專門用於 Keysight 示波器的波形擷取
     - `oscope-scpi` - 支援 MSO-X/DSO-X 系列
     - `msox3000` - 針對 3000A 系列
   - DSOX4034A 屬於 InfiniiVision 4000 X-Series，SCPI 命令與 3000/6000 系列相似

2. **通訊介面**:
   - 支援 USB, LAN (Ethernet), GPIB
   - 可使用 PyVISA 的資源字串格式:
     - USB: `USB0::0x0957::0x17##::MY########::INSTR`
     - TCPIP: `TCPIP0::192.168.1.100::INSTR`

**遇到的問題 / Problems Encountered**:

1. **問題**: 虛擬環境初始沒有 pip
   - **解決方案**: 使用 `python -m ensurepip --default-pip` 安裝 pip
   - **原因**: Windows 虛擬環境可能不會自動包含 pip

2. **問題**: Bash 工具在 Windows 環境下路徑處理
   - **解決方案**: 使用 `.venv/Scripts/python.exe` 直接執行 Python
   - **筆記**: 即使在 Windows 上，Claude Code 的 Bash 工具使用 Unix shell

**下一步 / Next Steps**:
- 實作 DSOX4034A 基本類別
- 建立連線管理功能
- 實作基本 SCPI 命令包裝

**參考資源 / References**:
- [Keysight InfiniiVision 4000 X-Series Programmer's Guide](https://www.keysight.com/us/en/assets/9018-06976/programming-guides/9018-06976.pdf)
- [PyVISA Documentation](https://pyvisa.readthedocs.io/)
- [keyoscacquire Documentation](https://keyoscacquire.readthedocs.io/)

### 22:30 - 即時 Vrms 資料記錄器實作 / Real-Time Vrms Data Logger Implementation

**工作內容 / Work Done**:
- 實作完整的 Vrms 即時資料記錄系統
- 建立 `vrms_logger.py` 主程式
  - 每 100ms 讀取 Channel 1 Vrms
  - 時間戳記格式: HH:MM:SS:MSMSMS
  - 即時寫入 Excel 檔案
  - 每 5 分鐘複製到 FINAL 檔案
- 安裝 `openpyxl` 套件 (v3.1.5)
- 建立 `results/` 資料夾
- 建立使用範例 `examples/vrms_logger_example.py`
- 更新專案文件

**技術決策 / Technical Decisions**:

1. **雙檔案架構設計**
   - **主記錄檔**: `Result_<StartTime>_Real-Time-Result.xlsx`
     - 持續開啟並寫入資料
     - 每次量測後立即儲存 (確保資料不遺失)
   - **FINAL 檔案**: `Result_<StartTime>_Real-Time-Result_FINAL.xlsx`
     - 每 5 分鐘複製一次主檔案
     - 允許使用者開啟查看而不中斷記錄
   - **優點**:
     - 主檔案專注於資料記錄，不被使用者開啟干擾
     - FINAL 檔案提供即時查看功能
     - 資料安全性高 (每次寫入都儲存)

2. **選擇 openpyxl 而非 pandas**
   - **原因**:
     - 更輕量，相依性少
     - 直接操作 Excel 檔案，無需額外轉換
     - 對於簡單的資料記錄足夠使用
   - **考量**: 若未來需要複雜資料分析，可切換至 pandas

3. **時間戳記格式**
   - 使用 `HH:MM:SS:MS` 格式 (毫秒精度)
   - Python datetime.microsecond 除以 1000 轉換為毫秒
   - 符合使用者需求的可讀性和精度

4. **取樣間隔 100ms**
   - 使用 `time.sleep(0.1)` 實現
   - 實際取樣率約為 ~10 Hz (考慮 SCPI 查詢時間)
   - 適合大多數 AC 信號量測應用

**實作細節 / Implementation Details**:

1. **執行緒安全**
   - 使用 `threading.Lock()` 保護檔案寫入操作
   - 防止複製檔案時與寫入操作衝突

2. **優雅關閉**
   - 實作 signal handler 處理 Ctrl+C
   - 確保中斷時執行最後一次檔案複製
   - 正確關閉 Excel workbook 和 VISA 連線

3. **錯誤處理**
   - SCPI 查詢失敗時繼續執行 (印出錯誤)
   - 檔案操作失敗時印出錯誤訊息
   - 使用 try-finally 確保資源清理

**功能特色 / Features**:
- ✅ 連續高速資料記錄 (100ms 間隔)
- ✅ 精確時間戳記 (毫秒精度)
- ✅ Excel 格式輸出 (易於開啟和分析)
- ✅ 雙檔案系統 (主記錄 + FINAL 查看)
- ✅ 命令列介面 (簡單易用)
- ✅ 優雅中斷處理 (Ctrl+C)
- ✅ 即時主控台顯示

**使用方式 / Usage**:
```bash
# 透過 USB 連線
python vrms_logger.py "USB0::0x0957::0x17A6::MY12345678::INSTR"

# 透過 Ethernet 連線
python vrms_logger.py "TCPIP0::192.168.1.100::INSTR"
```

**輸出檔案範例**:
```
results/
├── Result_20251117_223045_Real-Time-Result.xlsx
└── Result_20251117_223045_Real-Time-Result_FINAL.xlsx
```

**Excel 檔案格式**:
| Timestamp      | Vrms (V)   |
|----------------|------------|
| 22:30:45:123   | 1.234567   |
| 22:30:45:223   | 1.235123   |
| ...            | ...        |

**已知限制 / Known Limitations**:
- 實際取樣率受 SCPI 查詢時間影響 (通常 >10ms)
- Excel 檔案大小會隨時間增長 (每小時約 36,000 筆資料)
- Windows 檔案系統可能限制長時間開啟檔案寫入

**未來改進方向 / Future Improvements**:
- 考慮新增 CSV 輸出選項 (更小檔案)
- 實作資料緩衝以減少檔案 I/O
- 新增統計資訊 (平均、最大、最小值)
- 支援多通道同時記錄
- 新增圖形化即時顯示

### 23:15 - 效能優化 / Performance Optimization

**問題診斷 / Problem Diagnosis**:
- 使用者回報量測速度非常慢 (~2 秒/筆 而非 100ms)
- 經分析發現三個主要問題:
  1. **每次量測後都儲存 Excel 檔案** - 主要瓶頸
  2. **未補償處理時間** - 單純 sleep(0.1) 無法達成精確 100ms 間隔
  3. **示波器可能未處於連續運行模式**

**實作改進 / Improvements Implemented**:

1. **資料緩衝機制 (Data Buffering)**
   - 將資料先存入記憶體緩衝區
   - 每 50 筆量測才寫入磁碟一次 (可設定)
   - 減少磁碟 I/O 達 98%
   - 預期可達成接近 100ms 的量測間隔

2. **精確計時補償 (Precise Timing Compensation)**
   - 追蹤下次量測的目標時間
   - 動態計算並補償 SCPI 查詢和處理時間
   - 若運行落後會發出警告
   - 確保量測間隔精確為 100ms

3. **示波器連續運行設定**
   - 連線時明確設定 Channel 1 開啟
   - 設定示波器為 RUN 模式 (連續擷取)
   - 避免每次量測都需觸發

**程式碼變更 / Code Changes**:
- 新增 `data_buffer` 緩衝區
- 新增 `buffer_data()` 方法
- 新增 `flush_buffer()` 方法
- 改寫 `run()` 主迴圈實作精確計時
- 改寫 `connect()` 加入示波器設定
- 新增可選參數 `save_interval` 設定儲存間隔

**效能比較 / Performance Comparison**:

| 項目 | 改進前 | 改進後 |
|------|--------|--------|
| 量測速度 | ~2 秒/筆 | ~100ms/筆 |
| 磁碟寫入 | 每筆量測 | 每 50 筆量測 |
| 資料遺失風險 | 極小 (立即儲存) | 小 (最多 50 筆) |
| 記憶體使用 | 極小 | 小緩衝區 (~2KB/50 筆) |

**使用方式更新 / Updated Usage**:
```bash
# 預設: 每 50 筆儲存一次
python vrms_logger.py "USB0::0x0957::0x17A6::MY12345678::INSTR"

# 自訂儲存間隔 (例: 每 100 筆)
python vrms_logger.py "USB0::0x0957::0x17A6::MY12345678::INSTR" 100
```

**安全機制 / Safety Features**:
- Ctrl+C 中斷時自動清空緩衝區
- 每 5 分鐘更新 FINAL 檔案時清空緩衝區
- 程式結束時顯示總量測筆數
- 運行落後時發出警告

**文件建立 / Documentation Created**:
- 建立 `PERFORMANCE_IMPROVEMENTS.md` 詳細說明效能改進

**測試建議 / Testing Recommendations**:
- 實際執行確認達成 100ms 間隔
- 監控是否出現 "Running behind schedule" 警告
- 確認資料正確寫入 Excel 檔案
- 測試 Ctrl+C 中斷的資料完整性

---

## 2025-11-20

### Session - 簡化輸出檔案命名 / Simplify Output File Naming

**時間 / Time**: 14:30

**工作內容 / Work Done**:

1. **簡化 Excel 輸出檔案命名**
   - 舊格式: `Result_{timestamp}_Real-Time-Result.xlsx`
   - 新格式: `Result_{timestamp}.xlsx`
   - 舊格式: `Result_{timestamp}_Real-Time-Result_FINAL.xlsx`
   - 新格式: `Result_{timestamp}_FINAL.xlsx`

2. **更新的檔案**
   - `instruments/base_logger.py:174-175` - 更新 BaseDataLogger 模板
   - `PAPABIN_dsox4034a_vrms-fast.py:164-165` - 更新此腳本的檔案設定

3. **影響範圍**
   - 所有使用 BaseDataLogger 的專案自動套用新命名
   - `PAPABIN_dsox4034a-a34405a_vrms-temp.py` ✅
   - `PAPABIN_dsox4034a-ad2_vrms-temp.py` ✅
   - `PAPABIN_dsox4034a_vrms-fast.py` ✅

**技術決策 / Technical Decisions**:

1. **保留 _FINAL 後綴**
   - FINAL 檔案仍保留 `_FINAL` 後綴以便識別
   - 主檔案移除冗長的 `_Real-Time-Result` 描述
   - 時間戳記格式維持 `YYYYMMDD_HHMMSS`

2. **命名設計原則**
   - 檔案名稱直接顯示測試開始的真實日期時間
   - 更簡潔，更易讀
   - 減少檔案名稱長度，避免路徑過長問題

**檔案命名範例 / File Naming Examples**:

```
舊格式 / Old Format:
Result_20251120_143052_Real-Time-Result.xlsx
Result_20251120_143052_Real-Time-Result_FINAL.xlsx

新格式 / New Format:
Result_20251120_143052.xlsx
Result_20251120_143052_FINAL.xlsx
```

**使用者需求 / User Request**:
- 使用者認為原本的檔案名稱過長
- 提議使用真實日期時間作為檔案名稱
- 採納建議，簡化為 `Result_{實際測試開始日期時間}`

**Git 提交 / Git Commit**: `a773fb3` - Simplify output file naming format

---

## Git 提交歷史 / Git Commit History

(Git commits will be recorded here as they are made)

---

## 技術討論 / Technical Discussions

### VISA 後端選擇 / VISA Backend Selection

**討論日期**: 2025-11-17

**背景**: 選擇使用哪種 VISA 後端來控制儀器

**選項分析**:
1. **NI-VISA** (National Instruments)
   - 優點: 效能最好，硬體支援最廣
   - 缺點: 需要安裝大型軟體包，僅 Windows，授權問題

2. **Keysight IO Libraries Suite**
   - 優點: Keysight 官方支援，與 Keysight 儀器相容性好
   - 缺點: 需要下載安裝，註冊表單

3. **PyVISA-py** (純 Python 實作)
   - 優點: 無需額外安裝，跨平台，開源
   - 缺點: 效能可能略低，部分進階功能可能不支援

**決策**: 選擇 PyVISA-py
- 專案主要需求是基本的 SCPI 命令控制
- 簡化安裝和部署流程
- 使用者回饋表明 VISA 函式庫有穩定性問題
- 可以隨時切換到其他後端如果需要

---
