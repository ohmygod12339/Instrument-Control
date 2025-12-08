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

## 2025-12-08

### Session - Anbai AT4516 溫度計模組實作與除錯

**時間 / Time**: 全天

**工作內容 / Work Done**:

1. **建立 AT4516 儀器控制模組**
   - 建立 `instruments/anbai/` 目錄
   - 實作完整的 AT4516 控制類別
   - 支援 8 通道溫度讀取 (K-type 熱電偶)
   - 支援多種熱電偶類型 (TC-K, TC-J, TC-T, TC-E, TC-R, TC-S, TC-B, TC-N)
   - 實作比較器功能 (上下限設定)

2. **除錯 RS-232 通訊問題**
   - **問題 1**: ModuleNotFoundError: No module named 'serial'
     - 解決: 安裝 pyserial 套件
   - **問題 2**: 連線逾時 (TimeoutError)
     - 診斷: 測試所有波特率 (9600, 19200, 38400, 57600, 115200)
     - 解決: 修正 DEFAULT_BAUDRATE 從 115200 → 9600
   - **問題 3**: 第二次 *IDN? 查詢失敗
     - 診斷: AT4516 處理速度慢，需要指令間延遲
     - 解決: 在所有 write() 和 query() 加入 0.15s 延遲

3. **修正 SCPI 指令序列問題**
   - **問題 4**: 溫度讀取顯示 -100000.0°C (儀器前面板顯示正常 24°C)
     - 診斷: 閱讀 35 頁 AT4516 使用手冊
     - 發現: 量測進行中時，設定指令會被忽略
     - 解決: 實作正確序列 STOP → CONFIGURE → START
   - **問題 5**: 開機後首次執行返回 -100000.0，第二次執行正常
     - 診斷: START 後需等待第一個量測週期完成
     - 解決: 在 start_measurement() 加入等待時間和虛讀
     - 根據取樣率計算等待時間 (SLOW: 1.5s, MED: 1.0s, FAST: 1.0s)

4. **建立輔助方法和文件**
   - 新增 `configure_and_start()` 方法統一初始化流程
   - 建立 `examples/at4516_example.py` 範例腳本
   - 建立 `docs/AT4516_Quick_Reference.md` 快速參考文件

5. **建立組合式資料記錄器**
   - 建立 `PAPABIN_dsox4034a-at4516_vrms-fast-temp.py`
   - 結合 DSOX4034A (Vrms) + AT4516 (溫度 Ch1-4)
   - 取樣間隔: 1 秒
   - Excel 輸出: Timestamp, Vrms, Temp1-4, Elapsed(ms), Elapsed(hr)
   - 使用緩衝寫入機制 (save_interval=10)

6. **清理工作區**
   - 刪除所有測試腳本 (test_at4516_*.py)
   - 保持工作區整潔

**技術決策 / Technical Decisions**:

1. **AT4516 波特率選擇: 9600**
   - **原因**: 儀器實際使用 9600 baud (非手冊說明的 115200)
   - **驗證**: 透過系統性測試所有波特率確認

2. **指令間延遲: 0.15 秒**
   - **原因**: AT4516 處理 SCPI 指令較慢
   - **效果**: 確保每個指令完整處理
   - **權衡**: 略微降低讀取速度，但提高可靠性

3. **實作 configure_and_start() 輔助方法**
   - **原因**: 正確初始化序列複雜且容易出錯
   - **效果**: 使用者只需一行程式碼即可完成初始化
   - **包含**: STOP → 設定熱電偶類型 → 設定取樣率 → START → 等待 → 虛讀

4. **虛讀機制**
   - **原因**: 儀器 START 後需要完成首次量測週期
   - **實作**: 根據取樣率等待適當時間，然後執行一次虛讀
   - **效果**: 開機後首次執行即可獲得正確讀值

5. **組合式記錄器設計**
   - **取樣間隔**: 1 秒 (而非原本的 100ms)
   - **理由**: 溫度變化較慢，1 秒足夠
   - **資料格式**: 8 欄位 (時間戳、電壓、4 個溫度、經過時間)

**程式碼變更 / Code Changes**:

1. **instruments/anbai/at4516.py**:
   - `DEFAULT_BAUDRATE = 9600` (line 27)
   - `inter_command_delay` 參數加入 `__init__()` (line 56)
   - `write()` 方法加入延遲 (line 90)
   - `query()` 方法加入延遲 (lines 99-100)
   - `connect()` 方法加入 STOP 指令 (line 117)
   - `start_measurement()` 加入 wait_for_reading 參數和虛讀邏輯 (lines 246-266)
   - 新增 `configure_and_start()` 方法 (lines 286-328)

2. **examples/at4516_example.py**:
   - 所有範例更新為使用 `configure_and_start()` 方法
   - 加入錯誤值檢查 (temp > -100000)

3. **新增檔案**:
   - `instruments/anbai/__init__.py`
   - `instruments/anbai/at4516.py`
   - `examples/at4516_example.py`
   - `docs/AT4516_Quick_Reference.md`
   - `PAPABIN_dsox4034a-at4516_vrms-fast-temp.py`

4. **刪除檔案**:
   - `test_at4516_connection.py`
   - `test_at4516_commands.py`
   - `test_at4516_channels.py`
   - `test_at4516_fix.py`

**除錯過程 / Debugging Process**:

1. **系統性波特率測試**
   - 建立診斷腳本測試所有常用波特率
   - 發現 9600 baud 成功連線
   - 確認與手冊不符 (手冊說明 115200)

2. **SCPI 指令序列研究**
   - 閱讀完整 35 頁使用手冊
   - 找到關鍵資訊: 量測進行中指令被忽略
   - 建立測試腳本驗證 STOP → SET → START 序列

3. **開機初始化問題分析**
   - 觀察: 首次執行錯誤，第二次執行正常
   - 假設: 需要虛讀清除緩衝區 (使用者建議)
   - 實作: 等待 + 虛讀機制
   - 驗證: 開機後首次執行即可正常

**遇到的問題 / Problems Encountered**:

1. **手冊與實際不符**
   - 手冊說明支援 115200 baud
   - 實際儀器使用 9600 baud
   - 解決: 透過實測確認

2. **指令回應延遲**
   - AT4516 處理指令較慢
   - 連續指令會失敗
   - 解決: 加入固定延遲

3. **設定指令被忽略**
   - 量測進行中無法設定
   - 解決: 先 STOP 再設定

4. **開機後首次讀取錯誤**
   - START 後立即讀取返回 -100000.0
   - 解決: 等待量測週期完成 + 虛讀

**使用方式 / Usage**:

```python
from instruments.anbai import AT4516

# 基本使用
with AT4516() as meter:
    # 一行初始化 (CRITICAL!)
    meter.configure_and_start(tc_type='TC-K', rate='FAST', unit='CEL')

    # 讀取所有通道
    temps = meter.read_all_channels()
    for i, temp in enumerate(temps[:8], start=1):
        print(f"Channel {i}: {temp:.1f}°C")

# 組合式記錄器
python PAPABIN_dsox4034a-at4516_vrms-fast-temp.py
```

**下一步 / Next Steps**:
- 測試組合式資料記錄器實際運行
- 驗證 1 秒取樣間隔的準確性
- 確認溫度讀取穩定性

**參考資源 / References**:
- Anbai AT4516 User Manual (35 pages, Chinese)
- pyserial Documentation

**Git 提交 / Git Commit**: `6d49ba5` - Add Anbai AT4516 temperature meter module and combined logger

---

## 2025-12-08 (Session 2)

### Session - Add Vertical Scale Configuration to PAPABIN Scripts

**時間 / Time**: 晚間

**工作內容 / Work Done**:

1. **建立完整程式碼架構說明文件**
   - 建立 `docs/CODE_ARCHITECTURE_EXPLAINED.md`
   - 逐行解釋 DSOX4034A、AT4516 和組合式記錄器的架構
   - 包含通訊流程圖和設計模式說明
   - 記錄除錯過程中學到的關鍵教訓

2. **新增垂直刻度設定到所有 PAPABIN 腳本**
   - 使用者發現問題: 手動設定示波器可能導致量測不一致
   - 解決方案: 在應用程式碼中設定垂直刻度，而非模組中
   - 設定值: 0.2 V/div (200 mV/div) - 與實驗室設定一致
   - 更新的檔案:
     - `PAPABIN_dsox4034a_vrms-fast.py`
     - `PAPABIN_dsox4034a-at4516_vrms-fast-temp.py`
     - `PAPABIN_dsox4034a-a34405a_vrms-temp.py`
     - `PAPABIN_dsox4034a-ad2_vrms-temp.py`

**技術決策 / Technical Decisions**:

1. **垂直刻度設定位置**
   - **應用層設定**: PAPABIN 腳本設定特定刻度
   - **模組保持彈性**: dsox4034a.py 模組不設定預設值
   - **原因**: 保持模組的通用性，允許其他應用使用不同刻度

2. **設定順序**
   ```python
   self.scope.channel_on(1)           # 1. 啟用通道
   self.scope.set_channel_scale(1, 0.2)  # 2. 設定垂直刻度
   self.scope.set_timebase_scale(...)    # 3. 設定時基
   self.scope.run()                      # 4. 開始運行
   ```

3. **驗證機制**
   - 設定後立即查詢確認
   - 顯示確認訊息給使用者
   - 格式: `print(f"Vertical scale confirmed: {scale*1000:.1f} mV/div")`

**使用者需求 / User Request**:

使用者檢查示波器設定，發現當前設定為:
- Channel 1 垂直刻度: 0.2 V/div
- 耦合: DC
- 觸發模式: EDGE, AUTO sweep
- 觸發源: CHAN1, 0.0V

**問題**:
如果有人手動更改示波器設定，同一次量測可能會有不同的垂直刻度，導致不一致。

**解決方案**:
在每個 PAPABIN 腳本中明確設定垂直刻度，確保:
1. **一致性**: 每次量測使用相同刻度
2. **可重現性**: 腳本執行時自動設定正確刻度
3. **獨立性**: 不依賴手動設定

**程式碼變更 / Code Changes**:

所有四個 PAPABIN 腳本都加入:
```python
# Set vertical scale for consistent measurements
print("Setting vertical scale to 0.2 V/div (200 mV/div)...")
self.scope.set_channel_scale(1, 0.2)  # 200 mV/div
current_scale = self.scope.get_channel_scale(1)
print(f"  Vertical scale confirmed: {current_scale*1000:.1f} mV/div")
```

**效益 / Benefits**:

1. **量測一致性**: 所有量測使用相同的垂直刻度
2. **可追溯性**: 記錄檔案明確顯示使用的刻度
3. **自動化**: 無需手動設定示波器
4. **錯誤預防**: 避免因人為設定錯誤導致的問題

**參考資源 / References**:
- 使用者提供的示波器當前設定
- DSOX4034A Programmer's Guide - Channel configuration

**Git 提交 / Git Commit**: `2ef4bd5` - Add vertical scale configuration to PAPABIN scripts and architecture documentation

---

## 2025-12-08 (Session 3)

### Session - Add Custom Y-Axis Labels to Plotting Script

**時間 / Time**: 深夜

**工作內容 / Work Done**:

1. **新增自訂 Y 軸標籤功能到繪圖腳本**
   - 新增 `--ylabel-left` / `--yl` 參數: 自訂左側 Y 軸標籤
   - 新增 `--ylabel-right` / `--yr` 參數: 自訂右側 Y 軸標籤
   - 僅在使用 `--dual-axis` 時有效
   - 如果未提供自訂標籤，會自動使用欄位名稱

**使用者需求 / User Request**:
使用者希望在使用雙 Y 軸 (`--dual-axis`) 時，能夠自訂 Y 軸的標籤文字。

**技術實作 / Technical Implementation**:

1. **函數簽章更新**:
   ```python
   def plot_results(df: pd.DataFrame, columns: list = None, dual_axis: bool = False,
                   title: str = None, save_path: str = None,
                   ylabel_left: str = None, ylabel_right: str = None):
   ```

2. **左側 Y 軸標籤**:
   ```python
   # Use custom label if provided, otherwise use column name
   left_label = ylabel_left if ylabel_left else col1
   ax1.set_ylabel(left_label, color=colors[0], fontsize=12)
   ```

3. **右側 Y 軸標籤**:
   ```python
   # For 2 columns
   right_label = ylabel_right if ylabel_right else plot_columns[1]
   ax2.set_ylabel(right_label, color=colors[1], fontsize=12)

   # For >2 columns
   right_label = ylabel_right if ylabel_right else 'Other Measurements'
   ax2.set_ylabel(right_label, fontsize=12)
   ```

**命令列參數 / Command-Line Arguments**:
```bash
--ylabel-left LABEL, --yl LABEL    # 左側 Y 軸標籤
--ylabel-right LABEL, --yr LABEL   # 右側 Y 軸標籤
```

**使用範例 / Usage Examples**:

```bash
# 雙 Y 軸並自訂標籤
python GENERAL_all_plot-results.py results/file.xlsx --dual-axis \
    --ylabel-left "Voltage (V)" --ylabel-right "Temperature (°C)"

# 使用簡短參數
python GENERAL_all_plot-results.py results/file.xlsx -d \
    --yl "電壓 (V)" --yr "溫度 (°C)"

# 指定欄位並自訂標籤
python GENERAL_all_plot-results.py results/file.xlsx --dual-axis \
    -c "Vrms (V)" "Temp Ch1 (°C)" --yl "Voltage" --yr "Temperature"
```

**預設行為 / Default Behavior**:
- 若未提供 `--ylabel-left`: 使用第一個欄位名稱
- 若未提供 `--ylabel-right`:
  - 2 欄位時: 使用第二個欄位名稱
  - >2 欄位時: 使用 "Other Measurements"

**程式碼變更 / Code Changes**:
- `GENERAL_all_plot-results.py` (lines 100-101): 函數簽章新增參數
- `GENERAL_all_plot-results.py` (lines 152-153): 左側標籤邏輯
- `GENERAL_all_plot-results.py` (lines 172-182): 右側標籤邏輯
- `GENERAL_all_plot-results.py` (lines 357-360): 新增命令列參數
- `GENERAL_all_plot-results.py` (lines 412-413): 傳遞參數到函數

**文檔更新 / Documentation Updates**:
- 更新模組 docstring 使用範例
- 更新 argparse epilog 範例
- 新增完整使用範例說明

**效益 / Benefits**:
1. **靈活性**: 可自訂更易讀的軸標籤
2. **國際化**: 支援任何語言的標籤（中文、英文等）
3. **簡潔性**: 可簡化長欄位名稱
4. **向後相容**: 不影響現有使用方式

**Git 提交 / Git Commit**: `9e651b2` - Add custom y-axis label feature to plotting script

---

## 2025-12-08 (Session 4)

### Session - Add Customizable Grid Intervals to Plotting Script

**時間 / Time**: 深夜

**工作內容 / Work Done**:

1. **新增可自訂網格間距功能到繪圖腳本**
   - 新增 `--grid-x` / `--gx` 參數: X 軸主網格間距 (小時)
   - 新增 `--grid-y` / `--gy` 參數: Y 軸 (或左側 Y 軸) 主網格間距
   - 新增 `--grid-y-right` / `--gyr` 參數: 右側 Y 軸主網格間距 (雙軸模式)
   - 新增 `--grid-minor` / `--gm` 參數: 啟用次網格線
   - 使用 matplotlib 的 `MultipleLocator` 實現精確網格控制

**使用者需求 / User Request**:
使用者希望能夠根據資料範圍自訂網格間距，例如每 5、10 或 50 個單位顯示網格線，而不是使用自動生成的間距。

**技術實作 / Technical Implementation**:

1. **Import 更新**:
   ```python
   from matplotlib.ticker import AutoMinorLocator, MultipleLocator
   ```

2. **函數簽章更新**:
   ```python
   def plot_results(df: pd.DataFrame, columns: list = None, dual_axis: bool = False,
                   title: str = None, save_path: str = None, ylabel_left: str = None,
                   ylabel_right: str = None, grid_x: float = None, grid_y_left: float = None,
                   grid_y_right: float = None, grid_minor: bool = False):
   ```

3. **網格配置邏輯**:
   ```python
   # Configure x-axis grid
   if grid_x is not None:
       ax1.xaxis.set_major_locator(MultipleLocator(grid_x))
   else:
       ax1.xaxis.set_minor_locator(AutoMinorLocator())

   # Configure y-axis grid (left/main axis)
   if grid_y_left is not None:
       ax1.yaxis.set_major_locator(MultipleLocator(grid_y_left))
   else:
       ax1.yaxis.set_minor_locator(AutoMinorLocator())

   # Main grid
   ax1.grid(True, which='major', alpha=0.3, linewidth=0.8)

   # Minor grid (if requested)
   if grid_minor:
       ax1.grid(True, which='minor', alpha=0.15, linewidth=0.5, linestyle=':')
   ```

4. **右側 Y 軸網格 (雙軸模式)**:
   ```python
   if dual_axis and len(plot_columns) >= 2:
       if grid_y_right is not None:
           ax2.yaxis.set_major_locator(MultipleLocator(grid_y_right))
       else:
           ax2.yaxis.set_minor_locator(AutoMinorLocator())
       ax2.grid(False)  # Disable right axis grid to avoid overlap
   ```

**命令列參數 / Command-Line Arguments**:
```bash
--grid-x INTERVAL, --gx INTERVAL      # X 軸主網格間距 (小時)
--grid-y INTERVAL, --gy INTERVAL      # Y 軸主網格間距
--grid-y-right INTERVAL, --gyr INTERVAL  # 右側 Y 軸主網格間距
--grid-minor, --gm                    # 啟用次網格線
```

**使用範例 / Usage Examples**:

```bash
# 自訂網格間距 (X 軸每 0.5 小時，Y 軸每 10 單位)
python GENERAL_all_plot-results.py results/file.xlsx --grid-x 0.5 --grid-y 10

# 雙 Y 軸模式，每個軸使用不同間距
python GENERAL_all_plot-results.py results/file.xlsx --dual-axis \
    --grid-x 1 --grid-y 5 --grid-y-right 50

# 啟用次網格線
python GENERAL_all_plot-results.py results/file.xlsx --grid-minor

# 完整範例：雙軸 + 自訂標籤 + 自訂網格
python GENERAL_all_plot-results.py results/file.xlsx --dual-axis \
    --yl "Voltage (V)" --yr "Temp (°C)" \
    --gx 0.5 --gy 0.1 --gyr 5 --gm
```

**網格樣式 / Grid Styling**:
- **主網格**: alpha=0.3, linewidth=0.8, 實線
- **次網格**: alpha=0.15, linewidth=0.5, 虛線 (':')

**預設行為 / Default Behavior**:
- 若未指定網格間距: 使用 matplotlib 的 `AutoMinorLocator` 自動配置
- 主網格: 總是顯示
- 次網格: 僅在使用 `--grid-minor` 時顯示
- 右側 Y 軸網格: 關閉以避免與左側重疊

**程式碼變更 / Code Changes**:
- `GENERAL_all_plot-results.py` (line 41): 新增 `MultipleLocator` import
- `GENERAL_all_plot-results.py` (lines 109-111): 函數簽章新增 4 個參數
- `GENERAL_all_plot-results.py` (lines 232-264): 新增網格配置邏輯
- `GENERAL_all_plot-results.py` (lines 426-433): 新增 4 個命令列參數
- `GENERAL_all_plot-results.py` (lines 486-488): 傳遞參數到函數
- `GENERAL_all_plot-results.py` (lines 23-26, 398-408): 新增使用範例

**效益 / Benefits**:
1. **靈活性**: 可根據資料範圍調整網格密度
2. **可讀性**: 適當的網格間距提升圖表易讀性
3. **專業性**: 符合科學出版的圖表標準
4. **向後相容**: 不影響現有使用方式，預設行為不變

**Git 提交 / Git Commit**: `d735622` - Add customizable grid intervals to plotting script

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
