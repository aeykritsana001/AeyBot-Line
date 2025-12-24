from flask import Flask, request
import requests
import json
import yfinance as yf
import datetime
import os

app = Flask(__name__)

# --- ใส่ Token ของคุณตรงนี้ ---
CHANNEL_ACCESS_TOKEN = 'VPTmQL/xntTwRHJrEo1tZHM3X654aT0I4WXJ0VTUhANV7OgubY0URND2DHlKAB8mawXUIhGNNilt9I2d4tECLQ+VEQ8fY0YemnTcbznRidFMcOEn/M70N0+xBpRm+ZvNmbXdUJo5QnHzkYcz/1eDPQdB04t89/1O/w1cDnyilFU='

def get_stock_news(symbol):
    try:
        if not symbol.endswith(".BK") and len(symbol) < 6 and not symbol.isalpha(): pass 
        ticker = yf.Ticker(symbol)
        news_list = ticker.news
        if not news_list:
            ticker = yf.Ticker(f"{symbol}.BK")
            news_list = ticker.news
        if not news_list: return f"❌ ไม่พบข่าว: {symbol}"

        msg = f"📰 ข่าว: {symbol.upper()}\n━━━━━━━━━━\n"
        count = 0
        for news in news_list:
            if count >= 3: break
            title = news.get('title', '-')
            link = news.get('link', '#')
            try:
                pub_time = datetime.datetime.fromtimestamp(news.get('providerPublishTime', 0))
                time_str = pub_time.strftime('%d/%m %H:%M')
            except: time_str = "-"
            msg += f"📌 {title}\n🕒 {time_str}\n🔗 {link}\n\n"
            count += 1
        return msg.strip()
    except Exception as e: return f"Error: {e}"

@app.route("/", methods=['GET'])
def home():
    return "AeyBot is Running OK!", 200

@app.route("/", methods=['POST'])
def webhook():
    payload = request.json
    events = payload.get('events', [])
    for event in events:
        if event['type'] == 'message' and event['message']['type'] == 'text':
            user_msg = event['message']['text'].strip()
            reply_token = event['replyToken']

            if user_msg.upper().startswith("NEWS ") or user_msg.startswith("ข่าว "):
                stock_name = user_msg.split(" ")[1].upper()
                reply_text = get_stock_news(stock_name)
                reply_message(reply_token, reply_text)
                
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
