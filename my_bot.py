import os
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"
VERIFY_TOKEN = "my_secure_verify_token_123"

PRODUCT_LINKS = {
    "link": "https://www.amazon.com/shop/daily.deals.for.her",
    "deals": "https://www.amazon.com/shop/daily.deals.for.her",
    "קישור": "https://www.amazon.com/shop/daily.deals.for.her"
}

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    return requests.post(url, json=payload).json()

def handle_event(sender_id, text):
    text = text.lower().strip()
    for keyword, link in PRODUCT_LINKS.items():
        if keyword in text:
            send_message(sender_id, f"Glad you asked! Here is the link: {link}")
            break

@app.route("/webhook", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Error", 403

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "instagram":
        for entry in data["entry"]:
            # טיפול בהודעות פרטיות
            if "messaging" in entry:
                for event in entry["messaging"]:
                    if event.get("message"):
                        handle_event(event["sender"]["id"], event["message"].get("text", ""))
            # טיפול בתגובות על פוסטים
            if "changes" in entry:
                for change in entry["changes"]:
                    if change.get("field") == "comments":
                        comment_text = change["value"].get("text", "")
                        from_id = change["value"]["from"]["id"]
                        handle_event(from_id, comment_text)
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
