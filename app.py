from flask import Flask, request
import requests
import json
import datetime
from GoogleNews import GoogleNews # เรียกใช้ Google News

app = Flask(__name__)

# --- ใส่ Token ของคุณตรงนี้ ---
CHANNEL_ACCESS_TOKEN = 'VPTmQL/xntTwRHJrEo1tZHM3X654aT0I4WXJ0VTUhANV7OgubY0URND2DHlKAB8mawXUIhGNNilt9I2d4tECLQ+VEQ8fY0YemnTcbznRidFMcOEn/M70N0+xBpRm+ZvNmbXdUJo5QnHzkYcz/1eDPQdB04t89/1O/w1cDnyilFU=

def get_stock_news(symbol):
    try:
        # ใช้ Google News แทน Yahoo
        googlenews = GoogleNews(period='1d', lang='en') # หาข่าวภาษาอังกฤษ (ถ้าอยากได้ไทยแก้เป็น 'th')
        
        # ค้นหาด้วยคำว่า "ชื่อหุ้น stock news" เพื่อความแม่น
        googlenews.search(f'{symbol} stock news')
        result = googlenews.result()

        if not result:
            return f"❌ ไม่พบข่าวของ: {symbol}"

        msg = f"📰 ข่าว: {symbol.upper()} (Google)\n━━━━━━━━━━\n"
        count = 0
        
        for news in result:
            if count >= 3: break
            
            title = news.get('title', '-')
            link = news.get('link', '#')
            date = news.get('date', '-') # Google ให้เวลามาเป็น text เลย (เช่น '1 hour ago')
            
            msg += f"📌 {title}\n🕒 {date}\n🔗 {link}\n\n"
            count += 1
            
        return msg.strip()

    except Exception as e:
        return f"Error: {e}"

@app.route("/", methods=['GET'])
def home():
    return "AeyBot News Service is Running!", 200

@app.route("/", methods=['POST'])
def webhook():
    payload = request.json
    events = payload.get('events', [])
    for event in events:
        if event['type'] == 'message' and event['message']['type'] == 'text':
            user_msg = event['message']['text'].strip()
            reply_token = event['replyToken']

            # เช็คคำสั่ง "ข่าว" หรือ "News"
            if user_msg.upper().startswith("NEWS ") or user_msg.startswith("ข่าว "):
                try:
                    stock_name = user_msg.split(" ")[1].upper()
                    reply_text = get_stock_news(stock_name)
                    reply_message(reply_token, reply_text)
                except:
                    reply_message(reply_token, "พิมพ์ชื่อหุ้นด้วยครับ เช่น 'ข่าว GULF'")

    return 'OK', 200

def reply_message(reply_token, text):
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {'replyToken': reply_token, 'messages': [{'type': 'text', 'text': text}]}
    requests.post(url, headers=headers, data=json.dumps(data))

if __name__ == "__main__":
    app.run()
