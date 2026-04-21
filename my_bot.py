from flask import Flask, request
import os

app = Flask(__name__)

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
    # אישור קבלת אירוע
    return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    # Render מחייב להקשיב לכתובת 0.0.0.0 ולפורט מהסביבה
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
