import os
import requests
from flask import Flask, request

app = Flask(__name__)

# הגדרות המערכת
PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6" # הטוקן המורחב שלך מה-Debugger
VERIFY_TOKEN = "my_secure_verify_token_123" # וודא שזה מה שמוגדר ב-Webhook בפייסבוק

# מילון הלינקים - כאן תוכל להוסיף מוצרים בעתיד
PRODUCT_LINKS = {
    "link": "https://www.amazon.com/shop/daily.deals.for.her",
    "deals": "https://www.amazon.com/shop/daily.deals.for.her",
    "קישור": "https://www.amazon.com/shop/daily.deals.for.her",
    "amazon": "https://www.amazon.com/shop/daily.deals.for.her"
}

def send_message(recipient_id, text):
    """שליחת הודעה חזרה למשתמש"""
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, json=payload)
    return response.json()

def handle_message(sender_id, message_text):
    """ניתוח ההודעה ושליחת התגובה המתאימה"""
    text = message_text.lower().strip()
    
    # חיפוש מילת מפתח במילון
    found_link = None
    for keyword, link in PRODUCT_LINKS.items():
        if keyword in text:
            found_link = link
            break
    
    if found_link:
        response_text = f"Glad you asked! Here is the link: {found_link}"
        send_message(sender_id, response_text)
    else:
        # הודעה למקרה שלא נמצאה מילת מפתח (מומלץ להשאיר באנגלית לקהל האמריקאי)
        response_text = "Hi! To get the link for our latest deals, just type 'link' or 'deals'."
        send_message(sender_id, response_text)

@app.route("/", methods=['GET'])
def verify():
    """אימות ה-Webhook מול פייסבוק"""
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args.get("hub.challenge"), 200
    return "Hello World", 200

@app.route("/", methods=['POST'])
def webhook():
    """קבלת הודעות חדשות מאינסטגרם"""
    data = request.get_json()
    if data["object"] == "instagram":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text", "")
                    handle_message(sender_id, message_text)
    return "ok", 200

if __name__ == "__main__":
    app.run(port=5000)
