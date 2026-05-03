import os, requests, csv
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxjmJ_am2QHMspFLAICEKcRzVTsu_KXwq20ZX4nUq0sIsGQORjuEPMZBhzEyx5h-CC0jYkdBcedk5/pub?output=csv"

def get_link_from_sheet(user_text):
    user_text_clean = user_text.strip().lower()
    print(f"DEBUG: Processing message: '{user_text_clean}'")
    try:
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
        # שימוש ב-utf-8-sig כדי להתגבר על תווים נסתרים של גוגל
        decoded_content = response.content.decode('utf-8-sig')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        
        for row in cr:
            if len(row) >= 2:
                # ניקוי רווחים ותווים לבנים מהטבלה
                keyword = row[0].replace('\u200b', '').strip().lower()
                link = row[1].strip()
                
                if keyword and keyword != "keyword": # דילוג על כותרת
                    if keyword in user_text_clean:
                        print(f"DEBUG: SUCCESS! Found '{keyword}' in sheet. Link: {link}")
                        return link
        print(f"DEBUG: No match found in sheet for text: '{user_text_clean}'")
    except Exception as e:
        print(f"DEBUG: Critical Error reading sheet: {e}")
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
    print(f"DEBUG: FB API Response: {r.status_code}")

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge", ""), 200
    data = request.get_json()
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            if "messaging" in entry:
                send_reply(entry["messaging"][0]["sender"]["id"], entry["messaging"][0].get("message", {}).get("text", ""))
            elif "changes" in entry:
                # טיפול בתגובה על פוסט
                val = entry["changes"][0]["value"]
                user_id = val.get("from", {}).get("id")
                text = val.get("text", "")
                if user_id and text:
                    send_reply(user_id, text)
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
