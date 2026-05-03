import os, requests, csv
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxjmJ_am2QHMspFLAICEKcRzVTsu_KXwq20ZX4nUq0sIsGQORjuEPMZBhzEyx5h-CC0jYkdBcedk5/pub?output=csv"

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge", ""), 200
    
    data = request.get_json()
    print(f"--- INCOMING DATA: {data} ---")
    
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            user_id = None
            msg_text = ""
            
            if "messaging" in entry:
                user_id = entry["messaging"][0]["sender"]["id"]
                msg_text = entry["messaging"][0].get("message", {}).get("text", "").lower().strip()
            elif "changes" in entry:
                val = entry["changes"][0]["value"]
                user_id = val.get("from", {}).get("id")
                msg_text = val.get("text", "").lower().strip()

            if user_id and msg_text:
                print(f"--- TARGET USER: {user_id}, MESSAGE: {msg_text} ---")
                
                # קריאת הטבלה ישירות בתוך הפונקציה למניעת בעיות סנכרון
                try:
                    res = requests.get(SHEET_CSV_URL)
                    content = res.content.decode('utf-8-sig')
                    rows = list(csv.reader(content.splitlines()))
                    
                    for row in rows:
                        if len(row) >= 2:
                            kw = row[0].strip().lower()
                            lnk = row[1].strip()
                            if kw and kw in msg_text:
                                print(f"--- !!! MATCH !!! SENDING: {lnk} ---")
                                fb_url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                                payload = {"recipient": {"id": user_id}, "message": {"text": f"Here is your link! ✨ {lnk}"}}
                                post_res = requests.post(fb_url, json=payload)
                                print(f"--- FB STATUS: {post_res.status_code} ---")
                                break
                except Exception as e:
                    print(f"--- ERROR: {e} ---")
                    
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
