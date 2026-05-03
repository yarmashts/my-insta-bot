import os, requests, csv, difflib
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxjmJ_am2QHMspFLAICEKcRzVTsu_KXwq20ZX4nUq0sIsGQORjuEPMZBhzEyx5h-CC0jYkdBcedk5/pub?output=csv"
VERIFY_TOKEN = "meow" # וודא שזה מה שכתבת במטא

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # שלב האישור מול פייסבוק
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Wrong token", 403
    
    data = request.get_json()
    print(f"--- EVENT RECEIVED: {data} ---")
    
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            user_id = None
            msg_text = ""
            
            if "messaging" in entry:
                user_id = entry["messaging"][0]["sender"]["id"]
                msg_text = entry["messaging"][0].get("message", {}).get("text", "")
            elif "changes" in entry:
                val = entry["changes"][0]["value"]
                user_id = val.get("from", {}).get("id")
                msg_text = val.get("text", "")

            if user_id and msg_text:
                # הלוגיקה החכמה שלנו (Fuzzy Match)
                res = requests.get(SHEET_CSV_URL)
                rows = list(csv.reader(res.content.decode('utf-8-sig').splitlines()))
                catalog = {row[0].strip().lower(): row[1].strip() for row in rows if len(row) >= 2}
                
                # חיפוש לינק
                final_link = None
                for kw in catalog:
                    if kw in msg_text.lower():
                        final_link = catalog[kw]
                        break
                
                reply = f"Found it! ✨ {final_link}" if final_link else "Hi! Check our shop: https://amazon.com/shop/daily.deals.for.her"
                requests.post(f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}",
                              json={"recipient": {"id": user_id}, "message": {"text": reply}})
                
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
