import os, requests, csv, difflib
from flask import Flask, request

app = Flask(__name__)

# נתוני גישה
PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxjmJ_am2QHMspFLAICEKcRzVTsu_KXwq20ZX4nUq0sIsGQORjuEPMZBhzEyx5h-CC0jYkdBcedk5/pub?output=csv"

def get_best_match(user_msg):
    user_msg = user_msg.lower().strip()
    print(f"!!! ANALYZING MESSAGE: '{user_msg}' !!!")
    try:
        res = requests.get(SHEET_CSV_URL)
        res.raise_for_status()
        content = res.content.decode('utf-8-sig')
        rows = list(csv.reader(content.splitlines()))
        
        # יצירת קטלוג מהטבלה
        catalog = {row[0].strip().lower(): row[1].strip() for row in rows if len(row) >= 2}
        keywords = list(catalog.keys())
        print(f"DEBUG: Keywords in sheet: {keywords}")

        # 1. חיפוש ישיר
        for kw in keywords:
            if kw and kw in user_msg:
                print(f"DEBUG: Found exact match: {kw}")
                return catalog[kw]

        # 2. חיפוש שגיאות כתיב (Fuzzy Match)
        for word in user_msg.split():
            matches = difflib.get_close_matches(word, keywords, n=1, cutoff=0.6)
            if matches:
                print(f"DEBUG: Fuzzy match found! '{word}' -> '{matches[0]}'")
                return catalog[matches[0]]
                
    except Exception as e:
        print(f"!!! ERROR READING SHEET: {e} !!!")
    return None

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge", ""), 200
    
    data = request.get_json()
    print(f"--- NEW EVENT RECEIVED: {data} ---")
    
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
                print(f"--- PROCESSING FOR SENDER {user_id}: {msg_text} ---")
                link = get_best_match(msg_text)
                
                # אם לא נמצא לינק, נשלח את החנות הכללית
                reply = f"Found it! ✨ {link}" if link else "Hi! Check out our best deals here: https://amazon.com/shop/daily.deals.for.her"
                
                fb_url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                requests.post(fb_url, json={"recipient": {"id": user_id}, "message": {"text": reply}})
                print(f"--- REPLY SENT TO {user_id} ---")
                
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
