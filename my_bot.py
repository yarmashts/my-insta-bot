import os, requests
from flask import Flask, request

app = Flask(__name__)

# הטוקן שלך (השתמש בזה שסידרנו קודם ב-Debugger)
PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"

def send_link(user_id):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": "Glad you asked! Here is the link: https://www.amazon.com/shop/daily.deals.for.her"}
    }
    r = requests.post(url, json=payload)
    print(f"Sent to {user_id}. Response: {r.text}")

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge", ""), 200
    
    data = request.get_json()
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            # טיפול בהודעה פרטית
            if "messaging" in entry:
                user_id = entry["messaging"][0]["sender"]["id"]
                send_link(user_id)
            # טיפול בתגובה על פוסט
            elif "changes" in entry:
                user_id = entry["changes"][0]["value"]["from"]["id"]
                send_link(user_id)
                
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
