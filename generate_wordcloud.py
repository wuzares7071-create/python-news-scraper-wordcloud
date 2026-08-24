import os
import glob
import json
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. 尋找並讀取 JSON 檔案
json_files = glob.glob("daily_news_*.json")
if not json_files:
    raise FileNotFoundError("請確保資料夾內有 daily_news_*.json 檔案！")

latest_json = sorted(json_files)[-1]
print(f"📖 讀取檔案：{latest_json}")

df = pd.read_json(latest_json, encoding='utf-8')

# 2. 中文斷詞與停用詞過濾
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

cut_text = tokenize(df['標題'] if '標題' in df.columns else df['title'])

# 3. 指定字型檔路徑 (Windows 也可用 'C:/Windows/Fonts/msjh.ttc')
font_path = "NotoSansCJKtc-Regular.otf"

# 4. 生成與顯示文字雲
wc = WordCloud(
    font_path=font_path,
    background_color='white',
    width=1000,
    height=500,
    max_words=100
).generate(cut_text)

# 儲存圖片供 README 展示
wc.to_file("wordcloud_result.png")
print("✅ 文字雲圖片已儲存為 wordcloud_result.png")

# 顯示圖片
plt.figure(figsize=(12, 6))
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()