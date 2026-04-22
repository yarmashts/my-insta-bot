from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# הטוקן שלך
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
        print(f"Error: {e}")
    return None

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == "my_secure_token_123":
        return request.args.get("hub.challenge")
    return "Failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Data received: {data}") # זה מה שיראה לך "תנועה" ב-Logs
    
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if "message" in messaging_event:
                    sender_id = messaging_event["sender"]["id"]
                    text = messaging_event["message"].get("text", "")
                    link = get_amazon_link(text)
                    if link:
                        send_message(sender_id, f"מצאתי! הנה הלינק: {link}")
                    else:
                        send_message(sender_id, "היי! תכתוב 'deals' כדי לקבל את רשימת המבצעים שלי.")
    
    return "OK", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": recipient_id}, "message": {"text": text}})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
