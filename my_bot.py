from flask import Flask, request
import os, requests, sys

app = Flask(__name__)

# הטוקן המעודכן שלך - הוטמע בהצלחה
PAGE_ACCESS_TOKEN = "IGAASOBszRVu9BZAFl1NHZAaYUlReWxQTHNCN3Mxb3ZAwemRndloyWDVmX0lTdklDVm1UWGJ0VEx4Ul9PQjBCYXV1WGk5QTNGQXJVTlpGbFFJbkpITEVXd196RGdFc0duN1lmRjRNX0dnVDg0WEcxc0JmZAThRczNJbWVHNUlxaHRXYwZDZD"

def get_amazon_link(keyword):
    try:
        if not os.path.exists('links.csv'): return None
        with open('links.csv', 'r', encoding='utf-8') as f:
            for line in f:
                if ',' in line:
                    key, link = line.strip().split(',', 1)
                    if key.lower().strip() in keyword.lower():
                        return link.strip()
    except Exception as e:
        print(f"CSV Error: {e}")
    return None

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == "my_secure_token_123":
            return request.args.get("hub.challenge")
        return "Fail", 403

    if request.method == 'POST':
        data = request.get_json()
        print(f"--- Incoming Data: {data}")
        sys.stdout.flush()
        
        try:
            if data.get("object") == "instagram":
                for entry in data.get("entry", []):
                    for messaging_event in entry.get("messaging", []):
                        sender_id = messaging_event["sender"]["id"]
                        if "message" in messaging_event:
                            user_text = messaging_event["message"].get("text", "").lower()
                            link = get_amazon_link(user_text)
                            
                            if link:
                                send_message(sender_id, f"הנה הלינק שחיפשת: {link}")
                            else:
                                send_message(sender_id, "היי! תכתוב 'deals' כדי לראות את המבצעים הכי חמים שלנו.")
        except Exception as e:
            print(f"Error processing message: {e}")
            sys.stdout.flush()
            
        return "OK", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    response = requests.post(url, json=payload)
    print(f"Send status: {response.status_code}, Response: {response.text}")
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
