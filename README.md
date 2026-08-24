# 📰 Python ETtoday 即時新聞爬蟲與熱門關鍵字文字雲 (News Scraper & WordCloud)

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()

一個基於 Python 的自動化新聞爬蟲與文字分析專案。專案透過爬取 ETtoday 即時新聞標題，自動進行繁體中文斷詞（Jieba Tokenization）與停用詞過濾，最後生成當日熱門新聞關鍵字的視覺化文字雲（WordCloud）。

適合做為 **Python 網路爬蟲**、**中文文字探勘 (Text Mining)** 以及 **ETL 資料處理管道** 的 Portfolio 展示範例。

---

## 💡 專案亮點 (Key Features)

* **輕量高效爬蟲**：採用 `Requests` 與 `BeautifulSoup4` 進行目標網頁結構化萃取。
* **SQLite 歷史去重與自動清理**：資料庫採用原生 `PRIMARY KEY (URL)` 設定，達成重複標題過濾，並具備滾動式舊資料自動清理機制 (TTL)。
* **靈活資料匯出**：支援將爬取的最新資料自動導出為 `JSON` 與 `CSV` 格式。
* **精準中文斷詞與停用詞過濾**：整合 `jieba` 中文斷詞引擎，並設定自訂新聞停用詞清單（如：快訊、影、爆等），提高關鍵字統計精準度。
* **高質感資料視覺化**：自動生成繁體中文視覺化文字雲圖表，協助快速掌握當日新聞趨勢。

---

## 🖼️ 成果展示 (Result Preview)

產出的當日新聞熱門關鍵字文字雲：

![WordCloud Result](wordcloud_result.png)

---

## 📂 目錄結構 (Project Structure)

```text
python-news-scraper-wordcloud/
│
├── daily_news_20260825.json    # 爬蟲產出的結構化新聞資料 (JSON 格式)
├── daily_news_20260825.csv     # 爬蟲產出的新聞資料 (CSV 格式)
├── news_database.db            # SQLite 本地資料庫 (儲存去重後的新聞)
├── generate_wordcloud.py       # 文字雲生成與視覺化主程式
├── news_scraper.py             # ETtoday 自動化爬蟲與 SQLite 寫入主程式
├── NotoSansTC-Regular.otf      # 繁體中文字型檔 (避免文字雲亂碼)
├── wordcloud_result.png        # 產出的文字雲成果圖
├── requirements.txt            # 專案依賴套件清單
└── README.md                   # 專案說明文件