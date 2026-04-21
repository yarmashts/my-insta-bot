from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- נתונים מעודכנים (הטוקן מהצילום האחרון שלך) ---
ACCESS_TOKEN = 'IGAASOBszRVu9BZAFixeTBGX0hMem9qU2dPbGNoT282WnNGc2xBSkVZASWpvcFlZAZADlyUEExeTZARWEk1QXU0ZAlN6cjRxd2NmNjVLMjAzbW5TS2w2eHAwNVludkMyV3gxZAkw4ZAjBJaW5qZAGtuUzFmWENUcjR3MkQ0ck12aU1DVUFUUQZDZD'
PAGE_ID = '17841430145150085'
VERIFY_TOKEN = 'YaronBot2026'

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return challenge, 200
    return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("נתונים התקבלו:", data)
    try:
        if 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    if change['field'] == 'comments':
                        comment_text = change['value']['text'].upper()
                        sender_id = change['value']['from']['id']
                        if 'LINK' in comment_text:
                            print(f"שולח הודעה ל: {sender_id}")
                            send_message(sender_id, "היי! הנה הקישור שביקשת: https://amazon.com/shop/your-link")
    except Exception as e:
        print(f"שגיאה: {e}")
    return 'EVENT_RECEIVED', 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, params=params, json=payload)
    print("תגובה ממטא:", response.json())

if __name__ == '__main__':
    app.run(port=5000)