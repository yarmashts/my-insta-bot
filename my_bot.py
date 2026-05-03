import os, requests, csv, difflib
from flask import Flask, request

app = Flask(__name__)

# וודא שהטוקן הזה עדיין תקף
PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxjmJ_am2QHMspFLAICEKcRzVTsu_KXwq20ZX4nUq0sIsGQORjuEPMZBhzEyx5h-CC0jYkdBcedk5/pub?output=csv"

def find_best_match(user_text, catalog):
    user_words = user_text.lower().split()
    keywords = list(catalog.keys())
    
    # בדיקה 1: האם מילה מהטבלה נמצאת בדיוק בתוך ההודעה?
    for word in user_words:
        if word in keywords:
            return catalog[word]
            
    # בדיקה 2: חיפוש "מילה קרובה" (טיפול בשגיאות כתיב)
    for word in user_words:
        matches = difflib.get_close_matches(word, keywords, n=1, cutoff=0.8)
        if matches:
            return catalog[matches[0]]
            
    return None

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge", ""), 200
    
    data = request.get_json()
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
                print(f"--- Processing message: '{msg_text}' from {user_id} ---")
                try:
                    res = requests.get(SHEET_CSV_URL)
                    content = res.content.decode('utf-8-sig')
                    rows = list(csv.reader(content.splitlines()))
                    
                    # בניית מילון מהטבלה
                    catalog = {}
                    for row in rows:
                        if len(row) >= 2:
                            catalog[row[0].strip().lower()] = row[1].strip()

                    link = find_best_match(msg_text, catalog)
                    
                    if link:
                        print(f"--- MATCH FOUND: {link} ---")
                        fb_url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                        payload = {"recipient": {"id": user_id}, "message": {"text": f"Found it! ✨ Here's your link: {link}"}}
                        requests.post(fb_url, json=payload)
                    else:
                        print(f"--- NO MATCH FOUND FOR: {msg_text} ---")

                except Exception as e:
                    print(f"--- ERROR: {e} ---")
                    
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
