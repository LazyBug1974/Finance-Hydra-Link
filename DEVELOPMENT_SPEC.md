# 📜 Finance-Hydra-Link 開發規格書 (DEVELOPMENT_SPEC.md)

## 1. 專案定義
- **專案名稱**：Finance-Hydra-Link (Ian 的私有數據爬蟲轉 API 系統)
- **核心目標**：建立一個輕量化中繼站，抓取 Investing.com 網頁中難以透過標準 HTTP Request 取得的數據，並轉換為簡潔的 CSV 格式 API。
- **部署平台**：預設為 Vercel (Python Runtime)，利用其 Serverless Function 特性達成 HTTP 帶參數呼叫。

## 2. 檔案結構 (預期)
- `/api/index.py`：主要的 API 處理器（Vercel 進入點）。
- `requirements.txt`：相依套件清單（必須包含 cloudscraper）。
- `mapping.json`：儲存 Code 與 URL 的映射關係。
- `LAZYBUG_LOG.md`：開發歷程紀錄（由懶惰蟲維護，繁體中文累加制）。
- `README.md`：API 呼叫說明文件。

## 3. 技術規格與邏輯
### A. 標的映射表 (Mapping Table)
- **美國標普500指數期貨** `SPXF`: indices/us-spx-500-futures-historical-data
- **費城半導體指數** `SOX`: indices/phlx-semiconductor-historical-data
- **黃金現貨美元** `XAU`: currencies/xau-usd-historical-data
- **白銀現貨 美元** `XAG`: currencies/xag-usd-historical-data
- **銅期貨** `HGH6`: commodities/copper-historical-data
- **西德州原油** `WTI`: commodities/crude-oil-historical-data
- **美國 30Y 公債殖利率** `US30Y`: rates-bonds/u.s.-30-year-bond-yield-historical-data
- **美國 20Y 公債殖利率** `US20Y`: rates-bonds/us-20-year-bond-yield-historical-data
- **美國 10Y 公債殖利率** `US10Y`: rates-bonds/u.s.-10-year-bond-yield-historical-data
- **美國 2Y 公債殖利率** `US2Y`: rates-bonds/u.s.-2-year-bond-yield-historical-data

### B. 核心功能邏輯
1. **參數處理與抓取路徑**：
   - **當 `date=now` 時 (即時優先)**：
     - **必須**抓取網頁最上方的「大字即時報價」區域數值。
     - **嚴禁**抓取下方歷史表格的第一列數據。
     - 輸出日期應為網頁顯示的最新報價時間戳（僅保留日期部分 YYYY/MM/DD）。
   - **當 `date=YYYY/MM/DD` 時 (歷史優先)**：
     - 從下方的「歷史數據表格」中搜尋對應日期。
     - 抓取該列的 **「收市 (Close)」** 欄位數值。

2. **反爬蟲機制**：
   - 必須使用 `cloudscraper` 繞過 Cloudflare，並模擬真實 `User-Agent`。

3. **數據清洗與格式化**：
   - **數值處理**：移除所有千分號（範例：`5,000.13` 轉為 `5000.13`）。
   - **日期對齊**：輸出格式固定為 `[數據日期],[數值]`。
   - **重要規範**：輸出日期必須是數據對應的實際觀測日，嚴禁使用系統當前時間。

## 4. GitHub 配置
- **自動部署**：連動 Vercel，確保代碼 Push 後自動更新。
- **驗收標準**：懶惰蟲須確保部署後的 API URL 可成功回傳數據（綠燈狀態）。

## 5. 狀態：Approved
- **核准日期**：2026-02-20

- **核准人**：Ian
