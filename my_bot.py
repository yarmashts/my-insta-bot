from flask import Flask, request
import os
import requests

app = Flask(__name__)

# הטוקן הסודי שלך
PAGE_ACCESS_TOKEN = "IGAASOBszRVu9BZAGE5R3IxbGZAMMkwtQk5TZAzNIdnFfUy1Mel9ubnlndUtfRURLa3lsRnBtVDMtNFQxOHpVNkpGX1JRR2UxSFBrcTJudUxvLXlKV1VxYmdWcEJwdHppaEJzU1ZA4dHlSWC1DY3lZAQURwRkxPaU1BV2Q3OV9GdVluZAwZDZD"

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == "my_secure_token_123":
        return challenge, 200
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            if "messaging" in entry:
                for event in entry["messaging"]:
                    if "message" in event:
                        sender_id = event["sender"]["id"]
                        # בדיקה פשוטה: הבוט יענה לכל הודעה כדי לאשר שהוא חי
                        send_message(sender_id, "הקוד עובד! הסוכן שלך בענן מוכן!")
    return "EVENT_RECEIVED", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    response = requests.post(url, json=payload)
    print(f"Response: {response.status_code}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
