# 待辦事項與想法 / Todo and Ideas

本文件用於記錄臨時想法、研究主題、未來改進等靈活的項目。

This document records temporary ideas, research topics, future improvements, and flexible items.

---

## 待研究 / Research Topics

### 儀器控制相關 / Instrument Control Related

- [ ] 研究其他常見實驗室儀器的控制方式
  - 電源供應器 (Power Supplies)
  - 訊號產生器 (Signal Generators)
  - 數位萬用表 (Digital Multimeters)
  - 頻譜分析儀 (Spectrum Analyzers)

- [ ] 調查是否需要實作非同步控制
  - 多儀器同時控制
  - 長時間資料擷取

- [ ] 研究波形資料處理和視覺化選項
  - Matplotlib 整合
  - 即時波形顯示
  - 資料匯出格式 (CSV, HDF5, etc.)

### 效能優化 / Performance Optimization

- [ ] 比較不同 VISA 後端的效能差異
- [ ] 測試大量資料擷取的效能瓶頸
- [ ] 考慮使用批次命令減少通訊次數

### 錯誤處理與可靠性 / Error Handling and Reliability

- [ ] 研究儀器斷線重連機制
- [ ] 研究命令逾時處理策略
- [ ] 考慮實作命令佇列和重試機制

## 功能想法 / Feature Ideas

### 近期 / Near-term

- [ ] 新增儀器自動探測功能 (掃描可用的 VISA 資源)
- [ ] 建立設定檔系統 (儲存儀器連線設定)
- [ ] 實作基本的日誌記錄功能

### 中期 / Mid-term

- [ ] 建立圖形化使用者介面 (GUI)
  - 可考慮使用 PyQt, Tkinter, 或 web-based (Dash/Streamlit)
- [ ] 實作測試序列功能 (自動化測試腳本)
- [ ] 新增資料自動儲存和時間戳記

### 長期 / Long-term

- [ ] 開發儀器抽象層，提供統一的 API
- [ ] 建立儀器模擬器用於離線開發和測試
- [ ] 考慮支援遠端控制 (透過網路控制儀器)

## 文件改進 / Documentation Improvements

- [ ] 為每個儀器模組建立詳細的 API 文件
- [ ] 新增更多使用範例
- [ ] 建立疑難排解指南
- [ ] 新增常見問題 FAQ

## 測試相關 / Testing Related

- [ ] 建立單元測試框架
- [ ] 實作模擬測試 (mock testing) 不需要真實儀器
- [ ] 建立整合測試套件
- [ ] 設定持續整合 (CI) 流程

## 已知問題 / Known Issues

(目前無已知問題)

(No known issues currently)

## 參考連結 / Reference Links

- [PyVISA Examples](https://pyvisa.readthedocs.io/en/latest/introduction/example.html)
- [SCPI Command Reference](https://www.ivifoundation.org/docs/scpi-99.pdf)
- [Keysight Community Forum](https://community.keysight.com/)

## 封存 / Archive

### 2025-11-17
- ✅ 建立專案初始架構
- ✅ 研究 DSOX4034A 控制選項
- ✅ 安裝 PyVISA 和相關依賴

---

**管理原則 / Management Principles**:
- 自由添加想法，低門檻快速捕捉
- 定期檢視和優先排序
- 確認的任務移至 progress.md
- 完成或放棄的項目移至封存區

**Management principles**:
- Add ideas freely with low friction
- Review and prioritize periodically
- Move confirmed tasks to progress.md
- Archive completed or abandoned items
