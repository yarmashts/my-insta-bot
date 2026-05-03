import os, requests
from flask import Flask, request

app = Flask(__name__)

# הטוקן שלך (השתמש בזה שסידרנו קודם ב-Debugger)
PAGE_ACCESS_TOKEN = "EAANVeKYnEKQBRdEY5cKq03WOiOwrzS7QlZBBuOhblmiJHo70OT9gmLIOS3AXibZBMLz6GEzBIIGevoXFGUi3Yzj4CfOYxBkRijWuLvv7nHVXj3LctfOlkghR9ZAMl5CySUcFeRtj91X2IsjthpXJ52Y9RGdo0eQ46foCkw33ZAHLP1tHvB5Kqa6lbY2PoERhSZAasqsVUrNVaZBs7OQiFCWQZDZD"

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
