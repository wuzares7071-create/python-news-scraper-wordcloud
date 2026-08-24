import logging
import json
import sqlite3
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule

# 設定 Logging 紀錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)

class NewsPipeline:
    """
    ETtoday 新聞自動化 ETL 管道
    包含：爬取、去重、SQLite 寫入、歷史清理、CSV/JSON 匯出
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
        self.max_keep_records = max_keep_records  # 資料庫最多保留的新聞筆數
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
                link = "https://www.ettoday.net" + title_tag['href'] if title_tag['href'].startswith('/') else title_tag['href']

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
        """將資料寫入 SQLite 並去除重複，最後清理舊資料"""
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

            # 2. 保留最新 N 筆，刪除其餘舊資料
            cursor.execute('''
                DELETE FROM news
                WHERE rowid NOT IN (
                    SELECT rowid FROM news ORDER BY scraped_at DESC, news_time DESC LIMIT ?
                )
            ''', (self.max_keep_records,))

            conn.commit()

        logging.info(f"SQLite 更新完畢：新增 {new_inserted} 筆資料，舊資料已清理，目前資料庫維持最新 {self.max_keep_records} 筆。")
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

        # 終端機預覽輸出
        print(f"\n[即時更新 - {datetime.now().strftime('%H:%M:%S')}] 資料庫最新 {len(df)} 筆內容預覽：")
        print(df.head(5).to_string(index=False))

    def run_pipeline(self):
        """執行一次單次完整任務 (ETL)"""
        logging.info(">>> 開始執行新聞自動化抓取任務 <<<")
        html = self.fetch_page()
        if html:
            news_list = self.parse_news(html)
            self.save_to_db(news_list)
            self.export_files()


if __name__ == "__main__":
    pipeline = NewsPipeline(max_keep_records=50)

    # 1. 啟動時先立即執行第 1 次抓取
    pipeline.run_pipeline()

    # 2. 設定每 3 分鐘自動輪詢執行一次
    schedule.clear()
    schedule.every(3).minutes.do(pipeline.run_pipeline)

    print("\n⏰ 定時排程已啟動！每 3 分鐘會自動抓取一次... (按 Ctrl+C 可停止程式)")

    # 3. 常駐監聽排程（PyCharm 本地環境建議寫成無窮迴圈）
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停用排程，程式已安全結束。")