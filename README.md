# 📰 Python ETtoday 即時新聞爬蟲與熱門關鍵字文字雲 (News Scraper & WordCloud)

🔗 **Live Demo (歷史文字雲展示)**: [https://wuzares7071-create.github.io/python-news-scraper-wordcloud/](https://wuzares7071-create.github.io/python-news-scraper-wordcloud/)

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
├── .github/
│   └── workflows/
│       └── daily_scraper.yml          # GitHub Actions 每日自動排程與 CI/CD 部署設定檔
├── docs/                              # GitHub Pages 託管與前端動態展示資料夾
│   ├── images/                        # 歷史每日文字雲產出圖片 (wordcloud_YYYYMMDD.png)
│   ├── history.json                   # 自動生成的歷史日期索引檔 (提供前端選單動態讀取)
│   └── index.html                     # 響應式 (RWD) 歷史文字雲線上展示儀表板
├── news_database.db                   # SQLite 本地/雲端資料庫 (儲存歷史新聞、網址去重與維護最新100筆)
├── generate_wordcloud.py              # 中文斷詞 (Jieba) 與文字雲視覺化產出主程式
├── news_scraper.py                    # ETtoday 新聞爬蟲與 SQLite 寫入去重主程式
├── NotoSansCJKtc-Regular.otf          # 繁體中文字型檔 (確保文字雲正確渲染中文無亂碼)
├── requirements.txt                   # 專案 Python 套件依賴清單
├── README.md                          # 專案說明文件 (Portfolio 說明)
├── .gitignore                         # Git 版本控制忽略設定檔
├── daily_news_YYYYMMDD.json           # 每日爬取的結構化新聞資料 (JSON 格式範例)
├── daily_news_YYYYMMDD.csv            # 每日爬取的結構化新聞資料 (CSV 格式範例)
└── wordcloud_result.png               # 當日新聞關鍵字文字雲成果圖範例
