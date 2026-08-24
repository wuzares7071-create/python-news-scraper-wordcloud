import os
import glob
import json
from datetime import datetime
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ==========================================
# 1. 建立 docs 網頁檔案目錄結構
# ==========================================
docs_dir = "docs"
images_dir = os.path.join(docs_dir, "images")
history_json_path = os.path.join(docs_dir, "history.json")

os.makedirs(images_dir, exist_ok=True)

# ==========================================
# 2. 尋找並讀取最新產出的 JSON 資料
# ==========================================
json_files = glob.glob("daily_news_*.json")
# json_files = glob.glob("daily_news_20260824.json")
if not json_files:
    raise FileNotFoundError("找不到 daily_news_*.json 檔案，請先執行新聞爬蟲！")

latest_json = sorted(json_files)[-1]
print(f"📖 讀取最新新聞檔案：{latest_json}")
df = pd.read_json(latest_json, encoding='utf-8')

# ==========================================
# 3. 中文斷詞與停用詞處理
# ==========================================
stopwords = set([
    "快訊", "影", "爆", "新聞", "ETtoday", "報導", "記者", "表示",
    "指出", "今日", "預測", "最新", "曝光", "網友", "現場", "畫面"
])

def tokenize(text_list):
    words = []
    for title in text_list:
        tokens = jieba.cut(title)
        words.extend([w for w in tokens if len(w) > 1 and w not in stopwords])
    return " ".join(words)

title_column = '標題' if '標題' in df.columns else 'title'
cut_text = tokenize(df[title_column])

# ==========================================
# 4. 繪製文字雲並動態以日期命名存檔
# ==========================================
today_str = datetime.now().strftime("%Y%m%d")
# today_str = "20260824"
image_filename = f"wordcloud_{today_str}.png"
image_save_path = os.path.join(images_dir, image_filename)

font_path = "NotoSansCJKtc-Regular.otf"  # 請確保專案根目錄下有此字型檔，或使用系統字型路徑

wc = WordCloud(
    font_path=font_path if os.path.exists(font_path) else None,
    background_color='white',
    width=1000,
    height=500,
    max_words=100
).generate(cut_text)

wc.to_file(image_save_path)
print(f"✅ 已成功儲存文字雲圖片至：{image_save_path}")

# ==========================================
# 5. 自動寫入與更新 docs/history.json
# ==========================================
history_dates = []

# 若歷史 JSON 已存在則先讀取舊紀錄
if os.path.exists(history_json_path):
    try:
        with open(history_json_path, 'r', encoding='utf-8') as f:
            history_dates = json.load(f)
    except json.JSONDecodeError:
        history_dates = []

# 加入今天日期並去除重複、重新排序
if today_str not in history_dates:
    history_dates.append(today_str)

history_dates = sorted(list(set(history_dates)))

# 寫回 docs/history.json
with open(history_json_path, 'w', encoding='utf-8') as f:
    json.dump(history_dates, f, ensure_ascii=False, indent=4)

print(f"📝 已更新 {history_json_path}，目前包含的歷史日期：{history_dates}")