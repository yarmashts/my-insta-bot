from flask import Flask, request
import os
import requests

app = Flask(__name__)

# הטוקן שלך מוטמע כאן
PAGE_ACCESS_TOKEN = "IGAASOBszRVu9BZAGE5R3IxbGZAMMkwtQk5TZAzNIdnFfUy1Mel9ubnlndUtfRURLa3lsRnBtVDMtNFQxOHpVNkpGX1JRR2UxSFBrcTJudUxvLXlKV1VxYmdWcEJwdHppaEJzU1ZA4dHlSWC1DY3lZAQURwRkxPaU1BV2Q3OV9GdVluZAwZDZD"

def get_amazon_link(keyword):
    """מחפש מילת מפתח בקובץ הקישורים ומחזיר לינק"""
    try:
        # וודא שקיים קובץ בשם links.csv בתיקיה הראשית ב-GitHub
        if not os.path.exists('links.csv'):
            return None
        with open('links.csv', 'r', encoding='utf-8') as f:
            for line in f:
                if ',' in line:
                    key, link = line.strip().split(',', 1)
                    if key.lower().strip() in keyword.lower():
                        return link.strip()
    except Exception as e:
        print(f"Error reading links.csv: {e}")
    return None

@app.route('/webhook', methods=['GET'])
def verify():
    # אימות מול מטא
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == "my_secure_token_123":
        return challenge, 200
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            # טיפול בהודעות פרטיות (Messages)
            if "messaging" in entry:
                for event in entry["messaging"]:
                    if "message" in event:
                        sender_id = event["sender"]["id"]
                        text = event["message"].get("text", "")
                        link = get_amazon_link(text)
                        if link:
                            send_message(sender_id, f"הנה הלינק שביקשת: {link}")

            # טיפול בתגובות על פוסטים (Comments)
            if "changes" in entry:
                for change in entry["changes"]:
                    if change.get("field") == "comments":
                        comment_id = change["value"].get("id")
                        comment_text = change["value"].get("text", "")
                        link = get_amazon_link(comment_text)
                        if link:
                            # בתגובה לפוסט, אנחנו שולחים הודעה פרטית למגיב
                            user_id = change["value"]["from"]["id"]
                            send_message(user_id, f"ראיתי שביקשת לינק! הנה הוא: {link}")

    return "EVENT_RECEIVED", 200

def send_message(recipient_id, text):
    """שולח הודעה דרך ה-API של מטא"""
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, json=payload)
    print(f"Response from Meta: {response.status_code} - {response.text}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
