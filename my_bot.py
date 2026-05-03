import os, requests, csv
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"

# הקישור המדויק ששלחת
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxjmJ_am2QHMspFLAICEKcRzVTsu_KXwq20ZX4nUq0sIsGQORjuEPMZBhzEyx5h-CC0jYkdBcedk5/pub?output=csv"

def get_link_from_sheet(user_text):
    print(f"DEBUG: Searching for keyword in text: '{user_text}'")
    try:
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
        decoded_content = response.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        
        for row in cr:
            if len(row) >= 2:
                keyword = row[0].strip().lower()
                link = row[1].strip()
                if keyword and keyword in user_text.lower():
                    print(f"DEBUG: Match found! Keyword: {keyword}, Link: {link}")
                    return link
        print("DEBUG: No keyword match found in sheet.")
    except Exception as e:
        print(f"DEBUG: Error reading sheet: {e}")
    
    return None

def send_reply(user_id, text_received):
    target_link = get_link_from_sheet(text_received)
    
    # אם לא נמצא לינק בטבלה, הבוט לא ישלח סתם הודעה (כדי לא להספים)
    if not target_link:
        print("DEBUG: Skipping reply because no link was found.")
        return

    message_text = f"Found it! ✨ Check out the deal here: {target_link}"
    
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message_text}
    }
    r = requests.post(url, json=payload)
    print(f"DEBUG: Facebook API Response: {r.status_code} - {r.text}")

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge", ""), 200
    
    data = request.get_json()
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            user_id = None
            received_text = ""
            
            if "messaging" in entry:
                user_id = entry["messaging"][0]["sender"]["id"]
                received_text = entry["messaging"][0].get("message", {}).get("text", "")
            elif "changes" in entry:
                val = entry["changes"][0]["value"]
                user_id = val.get("from", {}).get("id")
                received_text = val.get("text", "")
            
            if user_id and received_text:
                send_reply(user_id, received_text)
                
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
