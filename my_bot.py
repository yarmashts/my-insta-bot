import os
import requests
from flask import Flask, request

app = Flask(__name__)

# הגדרות מפתח
PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"
VERIFY_TOKEN = "my_secure_verify_token_123"

PRODUCT_LINKS = {
    "link": "https://www.amazon.com/shop/daily.deals.for.her",
    "deals": "https://www.amazon.com/shop/daily.deals.for.her",
    "קישור": "https://www.amazon.com/shop/daily.deals.for.her"
}

def send_message(recipient_id, text):
    """פונקציה לשליחת הודעה עם בדיקת שגיאות"""
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    r = requests.post(url, json=payload)
    result = r.json()
    print(f"--- SEND ATTEMPT ---")
    print(f"Target ID: {recipient_id}")
    print(f"Facebook Response: {result}")
    return result

@app.route("/webhook", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Error", 403

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"--- INCOMING DATA ---")
    print(data)
    
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            # טיפול בהודעות פרטיות
            if "messaging" in entry:
                for event in entry["messaging"]:
                    if "message" in event and "text" in event["message"]:
                        sender_id = event["sender"]["id"]
                        msg_text = event["message"]["text"].lower()
                        for keyword, link in PRODUCT_LINKS.items():
                            if keyword in msg_text:
                                send_message(sender_id, f"Glad you asked! Here is the link: {link}")
            
            # טיפול בתגובות
            if "changes" in entry:
                for change in entry["changes"]:
                    if change.get("field") == "comments":
                        val = change.get("value", {})
                        if "from" in val:
                            from_id = val["from"]["id"]
                            comment_text = val.get("text", "").lower()
                            for keyword, link in PRODUCT_LINKS.items():
                                if keyword in comment_text:
                                    send_message(from_id, f"Thanks! Here is the link: {link}")
                                    
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
