from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "IGAASOBszRVu9BZAGE5R3IxbGZAMMkwtQk5TZAzNIdnFfUy1Mel9ubnlndUtfRURLa3lsRnBtVDMtNFQxOHpVNkpGX1JRR2UxSFBrcTJudUxvLXlKV1VxYmdWcEJwdHppaEJzU1ZA4dHlSWC1DY3lZAQURwRkxPaU1BV2Q3OV9GdVluZAwZDZD"

def get_amazon_link(keyword):
    try:
        if not os.path.exists('links.csv'):
            return None
        with open('links.csv', 'r', encoding='utf-8') as f:
            for line in f:
                if ',' in line:
                    key, link = line.strip().split(',', 1)
                    if key.lower().strip() in keyword.lower():
                        return link.strip()
    except Exception as e:
        print(f"CSV Error: {e}")
    return None

@app.route('/webhook', methods=['GET'])
def verify():
    # אימות ה-Webhook מול מטא
    if request.args.get("hub.verify_token") == "my_secure_token_123":
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Incoming data: {data}") # זה ידפיס לנו ב-Logs בדיוק מה מגיע
    
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if "message" in messaging_event:
                    sender_id = messaging_event["sender"]["id"]
                    user_text = messaging_event["message"].get("text", "").lower()
                    
                    link = get_amazon_link(user_text)
                    if link:
                        send_message(sender_id, f"הנה הלינק שביקשת: {link}")
                    else:
                        send_message(sender_id, "היי! תודה על ההודעה. כתוב 'deals' למבצעים.")
                        
    return "EVENT_RECEIVED", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    response = requests.post(url, json=payload)
    print(f"Send response: {response.status_code} - {response.text}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
