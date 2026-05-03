import os, requests, csv
from flask import Flask, request

app = Flask(__name__)

# וודא שהטוקן הזה עדיין תקף (EAAY...)
PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxjmJ_am2QHMspFLAICEKcRzVTsu_KXwq20ZX4nUq0sIsGQORjuEPMZBhzEyx5h-CC0jYkdBcedk5/pub?output=csv"

def get_link_from_sheet(user_text):
    user_text_clean = user_text.strip().lower()
    print(f"--- Processing incoming text: '{user_text_clean}' ---")
    try:
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
        decoded_content = response.content.decode('utf-8-sig')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        
        for row in cr:
            if len(row) >= 2:
                # ניקוי אגרסיבי של תווים נסתרים
                keyword = row[0].strip().lower().replace('\ufeff', '')
                link = row[1].strip()
                
                # אם המילה מהטבלה נמצאת בתוך מה שהמשתמש כתב
                if keyword and keyword != "keyword" and keyword in user_text_clean:
                    print(f"!!! MATCH FOUND !!! Keyword: {keyword} -> Link: {link}")
                    return link
        print(f"--- No match found in sheet for: '{user_text_clean}' ---")
    except Exception as e:
        print(f"--- SHEET ERROR: {e} ---")
    return None

def send_reply(user_id, text_received):
    target_link = get_link_from_sheet(text_received)
    if not target_link:
        return

    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": f"Found it! ✨ Check out the deal here: {target_link}"}
    }
    r = requests.post(url, json=payload)
    print(f"--- Facebook API Status: {r.status_code} ---")
    if r.status_code != 200:
        print(f"--- FB ERROR DETAIL: {r.text} ---")

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge", ""), 200
    
    data = request.get_json()
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            user_id = None
            msg_text = ""
            
            # בדיקה אם זו הודעה פרטית
            if "messaging" in entry:
                user_id = entry["messaging"][0]["sender"]["id"]
                msg_text = entry["messaging"][0].get("message", {}).get("text", "")
            # בדיקה אם זו תגובה על פוסט
            elif "changes" in entry:
                val = entry["changes"][0]["value"]
                user_id = val.get("from", {}).get("id")
                msg_text = val.get("text", "")
            
            if user_id and msg_text:
                send_reply(user_id, msg_text)
                
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
