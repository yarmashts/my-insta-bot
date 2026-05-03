import os, requests, csv
from flask import Flask, request

app = Flask(__name__)

# טוקן הגישה שלך
PAGE_ACCESS_TOKEN = "EAAYUPZBaU65sBOZC6h6qI5T7yR3Fv2lqXm880ZCAsZAn3X7RCDW683Bv3GZBsG8qZAyq77NfLnd8q8E4pE8U6hN9HshwZBM7rW8nI6fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6o7mX7mZA8fG3VZAy7mX2WnZCZA2ZC4ZA5ZCZAyZA6"

# הקישור המומר ל-CSV מהגוגל שיטס שלך
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxjmJ_am2QHMspFLAICEKcRzVTsu_KXwq20ZX4nUq0sIsGQORjuEPMZBhzEyx5h-CC0jYkdBcedk5/pub?output=csv"

def get_link_from_sheet(user_text):
    try:
        # פנייה לטבלה בגוגל
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
        decoded_content = response.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        
        # סריקת השורות בטבלה
        for row in cr:
            if len(row) >= 2:
                keyword = row[0].strip().lower()
                link = row[1].strip()
                # אם מילת המפתח מופיעה בטקסט של המשתמש
                if keyword and keyword in user_text.lower():
                    return link
    except Exception as e:
        print(f"Error fetching sheet: {e}")
    
    # לינק ברירת מחדל אם לא נמצאה התאמה
    return "https://amazon.com/shop/daily.deals.for.her"

def send_reply(user_id, text_received):
    target_link = get_link_from_sheet(text_received)
    
    # עיצוב ההודעה שתשלח לאינסטגרם
    message_text = f"Found it! ✨ Check out the deal here: {target_link}"
    
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message_text}
    }
    r = requests.post(url, json=payload)
    print(f"Sent to {user_id}. Status: {r.status_code}")

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge", ""), 200
    
    data = request.get_json()
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            user_id = None
            received_text = ""
            
            # זיהוי הודעה פרטית (DM)
            if "messaging" in entry:
                user_id = entry["messaging"][0]["sender"]["id"]
                received_text = entry["messaging"][0].get("message", {}).get("text", "")
            # זיהוי תגובה על פוסט
            elif "changes" in entry:
                val = entry["changes"][0]["value"]
                user_id = val.get("from", {}).get("id")
                received_text = val.get("text", "")
            
            if user_id and received_text:
                send_reply(user_id, received_text)
                
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
