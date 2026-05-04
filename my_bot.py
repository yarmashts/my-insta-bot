import os, requests, csv
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxjmJ_am2QHMspFLAICEKcRzVTsu_KXwq20ZX4nUq0sIsGQORjuEPMZBhzEyx5h-CC0jYkdBcedk5/pub?output=csv"
VERIFY_TOKEN = "meow"

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Verification failed", 403
    
    data = request.get_json()
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event:
                    msg_text = messaging_event["message"].get("text", "").lower()
                    
                    # חיפוש בטבלה
                    res = requests.get(SHEET_CSV_URL)
                    rows = list(csv.reader(res.content.decode('utf-8-sig').splitlines()))
                    link = None
                    for row in rows:
                        if len(row) >= 2 and row[0].strip().lower() in msg_text:
                            link = row[1].strip()
                            break
                    
                    final_reply = f"Found it! ✨ {link}" if link else "Visit our shop: https://amazon.com/shop/daily.deals.for.her"
                    
                    # שליחת הודעה
                    requests.post(
                        f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}",
                        json={"recipient": {"id": sender_id}, "message": {"text": final_reply}}
                    )
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
