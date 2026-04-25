from flask import Flask, request
import os, requests, sys

app = Flask(__name__)

# שים כאן את הטוקן החדש שייצרת הרגע עם כל ההרשאות
PAGE_ACCESS_TOKEN = "שים_כאן_את_הטוקן_החדש"

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

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == "my_secure_token_123":
            return request.args.get("hub.challenge")
        return "Fail", 403

    if request.method == 'POST':
        data = request.get_json()
        print(f"--- GOT MESSAGE ---")
        sys.stdout.flush()
        
        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for event in entry.get("messaging", []):
                    sender_id = event["sender"]["id"]
                    if "message" in event:
                        text = event["message"].get("text", "").lower()
                        link = get_amazon_link(text)
                        response_text = f"הנה הלינק: {link}" if link else "כתוב 'deals' למבצעים שלנו."
                        send_message(sender_id, response_text)
        return "OK", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    r = requests.post(url, json=payload)
    print(f"Send Result: {r.status_code} - {r.text}") # זה יגיד לנו בדיוק מה הבעיה
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
