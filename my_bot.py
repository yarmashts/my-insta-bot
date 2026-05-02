import os, requests, sys
from flask import Flask, request

app = Flask(__name__)

# הטוקן הנקי והאחרון שלך
PAGE_ACCESS_TOKEN = "EAANVeKYnEKQBRdEY5cKq03WOiOwrzS7QlZBBuOhblmiJHo70OT9gmLIOS3AXibZBMLz6GEzBIIGevoXFGUi3Yzj4CfOYxBkRijWuLvv7nHVXj3LctfOlkghR9ZAMl5CySUcFeRtj91X2IsjthpXJ52Y9RGdo0eQ46foCkw33ZAHLP1tHvB5Kqa6lbY2PoERhSZAasqsVUrNVaZBs7OQiFCWQZDZD".strip()

def get_amazon_link(keyword):
    try:
        if not os.path.exists('links.csv'): return None
        with open('links.csv', 'r', encoding='utf-8') as f:
            for line in f:
                if ',' in line:
                    key, link = line.strip().split(',', 1)
                    if key.lower().strip() in keyword.lower():
                        return link.strip()
    except: return None
    return None

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == "my_secure_token_123":
            return request.args.get("hub.challenge")
        return "Fail", 403

    if request.method == 'POST':
        data = request.get_json()
        print(f"DEBUG: Data received: {data}")
        sys.stdout.flush()
        
        # זיהוי הודעות אמיתיות ובדיקות
        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                # מבנה של הודעה אמיתית
                for messaging_event in entry.get("messaging", []):
                    sender_id = messaging_event["sender"]["id"]
                    if "message" in messaging_event:
                        process_message(sender_id, messaging_event["message"].get("text", ""))
                
                # מבנה של הודעת בדיקה (Test) מהממשק
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        value = change.get("value", {})
                        sender_id = value.get("sender", {}).get("id")
                        if sender_id:
                            process_message(sender_id, value.get("message", {}).get("text", ""))
        return "OK", 200

def process_message(sender_id, text):
    if not text: return
    print(f"DEBUG: Processing message from {sender_id}: {text}")
    link = get_amazon_link(text)
    response = f"הנה הלינק: {link}" if link else "היי! תכתוב 'deals' למבצעים."
    send_message(sender_id, response)

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    r = requests.post(url, json=payload)
    print(f"DEBUG: Send status {r.status_code}, Response: {r.text}")
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
