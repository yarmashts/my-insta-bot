from flask import Flask, request
import os, requests, sys

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "IGAASOBszRVu9BZAGE5R3IxbGZAMMkwtQk5TZAzNIdnFfUy1Mel9ubnlndUtfRURLa3lsRnBtVDMtNFQxOHpVNkpGX1JRR2UxSFBrcTJudUxvLXlKV1VxYmdWcEJwdHppaEJzU1ZA4dHlSWC1DY3lZAQURwRkxPaU1BV2Q3OV9GdVluZAwZDZD"

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
        print("--- GOT DATA FROM META ---")
        print(data)
        sys.stdout.flush() # מכריח את Render להראות את הלוג עכשיו!
        
        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for event in entry.get("messaging", []):
                    if "message" in event:
                        sid = event["sender"]["id"]
                        txt = event["message"].get("text", "").lower()
                        link = get_amazon_link(txt)
                        msg = f"הנה הלינק: {link}" if link else "כתוב 'deals' למבצעים."
                        send_message(sid, msg)
        return "OK", 200

def send_message(rid, txt):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    res = requests.post(url, json={"recipient": {"id": rid}, "message": {"text": txt}})
    print(f"Send status: {res.status_code}")
    sys.stdout.flush()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
