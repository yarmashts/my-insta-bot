from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "IGAASOBszRVu9BZAGE5R3IxbGZAMMkwtQk5TZAzNIdnFfUy1Mel9ubnlndUtfRURLa3lsRnBtVDMtNFQxOHpVNkpGX1JRR2UxSFBrcTJudUxvLXlKV1VxYmdWcEJwdHppaEJzU1ZA4dHlSWC1DY3lZAQURwRkxPaU1BV2Q3OV9GdVluZAwZDZD"

def get_amazon_link(keyword):
    try:
        if not os.path.exists('links.csv'): return None
        with open('links.csv', 'r', encoding='utf-8') as f:
            for line in f:
                if ',' in line:
                    key, link = line.strip().split(',', 1)
                    if key.lower().strip() in keyword.lower():
                        return link.strip()
    except Exception as e:
        print(f"CSV Error: {e}")
    return None

# דף הבית - כדי למנוע שגיאות 404 בבדיקות כלליות
@app.route('/')
def home():
    return "Bot is alive and listening!", 200

# נתיב ה-Webhook לאימות (GET) וקבלת הודעות (POST)
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == "my_secure_token_123":
            return request.args.get("hub.challenge")
        return "Verification failed", 403

    if request.method == 'POST':
        data = request.get_json()
        print(f"--- Incoming Data ---")
        print(data) # זה מה שיקפיץ את ה-Logs ב-Render
        
        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    if "message" in messaging_event:
                        sender_id = messaging_event["sender"]["id"]
                        user_text = messaging_event["message"].get("text", "")
                        link = get_amazon_link(user_text)
                        if link:
                            send_message(sender_id, f"הנה הלינק: {link}")
                        else:
                            send_message(sender_id, "היי! תכתוב 'deals' למבצעים שלי.")
        return "EVENT_RECEIVED", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
