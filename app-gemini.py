from flask import Flask, request, jsonify
import google.generativeai as genai
import requests, json
from load_creds import load_creds

creds = load_creds()

app = Flask(__name__)
#genai.configure(credentials=creds)
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash") # insert base or your tuned models here
page_id = 'YOUR_PAGE_ID'
access_token = 'YOUR_ACCESS_TOKEN'
graph_api = f'https://graph.facebook.com/v20.0/{page_id}/messages?access_token={access_token}'

VERIFY_TOKEN = 'hashscamai'

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def handle_message():
    payload = request.json
    message = payload['entry'][0]['messaging'][0]['message']
    sender_id = payload['entry'][0]['messaging'][0]['sender']['id']
    resp = model.generate_content(message['text'])
    data = {
    "recipient": {"id": sender_id},
    "messaging_type": "RESPONSE",
    "message": {"text": resp.text}
    }
    response = requests.post(graph_api, headers={"Content-Type": "application/json"}, data=json.dumps(data))

if __name__ == '__main__':
    app.run(port=3000, debug=False)