import logging
import json
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 設定 Logging 紀錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)


class NewsPipeline:
    """
    ETtoday 新聞自動化 ETL 管道 (GitHub Actions / 單次執行版)
    包含：爬取、去重、SQLite 寫入、維持最新 N 筆資料、CSV/JSON 匯出
    """

    def __init__(self, db_path: str = "news_database.db", max_keep_records: int = 100):
        self.target_url = "https://www.ettoday.net/news/news-list.htm"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self.db_path = db_path
        self.max_keep_records = max_keep_records  # 資料庫最多保留的新聞筆數 (設為 100 筆)
        self._init_db()

    def _init_db(self):
        """初始化 SQLite 資料庫與資料表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 以 url 作為 PRIMARY KEY 達成自動去重功能
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    url TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT,
                    news_time TEXT,
                    scraped_at TEXT
                )
            ''')
            conn.commit()

    def fetch_page(self) -> str | None:
        """發送 HTTP 請求並取得網頁原始碼"""
        try:
            logging.info(f"開始抓取網頁內容: {self.target_url}")
            response = requests.get(self.target_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"網絡請求失敗: {e}")
            return None

    def parse_news(self, html_content: str) -> list[dict]:
        """解析 HTML 結構"""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        news_list = []
        news_items = soup.select('.part_list_2 > h3')

        for item in news_items:
            try:
                time_str = item.select_one('.date').text.strip()
                category = item.select_one('em').text.strip()
                title_tag = item.select_one('a')

                title = title_tag.text.strip()
                link = "https://www.ettoday.net" + title_tag['href'] if title_tag['href'].startswith('/') else \
                title_tag['href']

                news_data = {
                    "time": time_str,
                    "category": category,
                    "title": title,
                    "url": link,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                news_list.append(news_data)

            except AttributeError:
                continue

        return news_list

    def save_to_db(self, news_list: list[dict]) -> int:
        """將資料寫入 SQLite 並去除重複，最後強制保留最新 N 筆 (預設 100 筆)"""
        if not news_list:
            return 0

        new_inserted = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 1. 寫入資料：若 url 已存在則忽略 (INSERT OR IGNORE)
            for news in news_list:
                cursor.execute('''
                    INSERT OR IGNORE INTO news (url, title, category, news_time, scraped_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (news['url'], news['title'], news['category'], news['time'], news['scraped_at']))

                if cursor.rowcount > 0:
                    new_inserted += 1

            # 2. 保留最新 N 筆，刪除超過 N 筆的舊資料
            cursor.execute('''
                DELETE FROM news
                WHERE rowid NOT IN (
                    SELECT rowid FROM news ORDER BY scraped_at DESC, news_time DESC LIMIT ?
                )
            ''', (self.max_keep_records,))

            conn.commit()

        logging.info(f"SQLite 更新完畢：新增 {new_inserted} 筆資料，資料庫維持最新 {self.max_keep_records} 筆上限。")
        return new_inserted

    def export_files(self):
        """從 SQLite 讀取最新資料並匯出成 CSV 與 JSON"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query("SELECT * FROM news ORDER BY scraped_at DESC, news_time DESC", conn)

        if df.empty:
            logging.warning("資料庫無內容，無法匯出。")
            return

        today_str = datetime.now().strftime("%Y%m%d")
        csv_filename = f"daily_news_{today_str}.csv"
        json_filename = f"daily_news_{today_str}.json"

        # 匯出 CSV (utf-8-sig 防止 Excel 亂碼)
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

        # 匯出 JSON
        records = df.to_dict(orient='records')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=4)

        logging.info(f"已匯出檔案: {csv_filename} 與 {json_filename}")

    def run_pipeline(self):
        """執行一次單次完整任務 (ETL)"""
        logging.info(">>> 開始執行新聞自動化抓取任務 <<<")
        html = self.fetch_page()
        if html:
            news_list = self.parse_news(html)
            self.save_to_db(news_list)
            self.export_files()
        logging.info(">>> 任務執行完畢，正常退出程式 <<<")


if __name__ == "__main__":
    # 設定資料庫最多保留最新 100 筆資料
    pipeline = NewsPipeline(max_keep_records=100)

    # 執行一次單次任務後即刻結束，無須常駐迴圈
    pipeline.run_pipeline()