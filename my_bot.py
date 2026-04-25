from flask import Flask, request
import os, requests, sys

app = Flask(__name__)

# הטוקן ל-60 יום שהפקת ב-Debugger - הוטמע כאן
PAGE_ACCESS_TOKEN = "IGAASOBszRVu9BZAFp6WXpjS0xlMkJ4S3otR0FWTUpsSUpjZAVl3VnZAmMlBLUU9fT2IwMEg1dl90TjJGM2xpejFGS1pDWGVMZADNrWGhpT0FUVlhGYVZAZAWGtOQkZALMjVOOVB3TEdBTlFqbVZAEYlJKYWJFNDdFb3FXOVluMS1GaFpqYwZDZD"

def get_amazon_link(keyword):
    try:
        # בדיקה אם קובץ הלינקים קיים בתיקייה הראשית
        if not os.path.exists('links.csv'): 
            print("CSV Error: links.csv file not found in root directory")
            return None
        with open('links.csv', 'r', encoding='utf-8') as f:
            for line in f:
                if ',' in line:
                    key, link = line.strip().split(',', 1)
                    if key.lower().strip() in keyword.lower():
                        return link.strip()
    except Exception as e:
        print(f"CSV Read Error: {e}")
    return None

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # אימות ראשוני מול מטא
        if request.args.get("hub.verify_token") == "my_secure_token_123":
            return request.args.get("hub.challenge")
        return "Fail", 403

    if request.method == 'POST':
        data = request.get_json()
        print(f"--- Incoming Data ---")
        sys.stdout.flush()
        
        try:
            if data.get("object") == "instagram":
                for entry in data.get("entry", []):
                    for messaging_event in entry.get("messaging", []):
                        sender_id = messaging_event["sender"]["id"]
                        
                        # טיפול בהודעת טקסט נכנסת
                        if "message" in messaging_event:
                            user_text = messaging_event["message"].get("text", "").lower()
                            print(f"User {sender_id} sent: {user_text}")
                            
                            link = get_amazon_link(user_text)
                            
                            if link:
                                response_text = f"הנה הלינק שחיפשת: {link}"
                            else:
                                response_text = "היי! תכתוב 'deals' או את שם המוצר כדי לקבל לינקים למבצעים הכי חמים שלנו."
                            
                            send_message(sender_id, response_text)
        except Exception as e:
            print(f"Error processing message: {e}")
            sys.stdout.flush()
            
        return "OK", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, json=payload)
    # הדפסה קריטית ללוגים כדי לוודא הצלחה (200)
    print(f"Send status: {response.status_code}, Response Body: {response.text}")
    sys.stdout.flush()

if __name__ == '__main__':
    # התאמה לפורט של Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
