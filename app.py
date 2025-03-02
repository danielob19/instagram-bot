# app.py - Bot para responder mensajes en Instagram y Messenger con Flask

from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

# Variables de entorno (Render)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN_MESSENGER = os.getenv("ACCESS_TOKEN_MESSENGER")
ACCESS_TOKEN_INSTAGRAM = os.getenv("ACCESS_TOKEN_INSTAGRAM")

@app.route('/webhook', methods=['GET'])
def verify():
    """Verifica el Webhook de Facebook e Instagram"""
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Token inválido", 403

@app.route('/webhook', methods=['POST'])
def receive_message():
    """Recibe y responde mensajes de Messenger e Instagram"""
    data = request.get_json()
    if "entry" in data:
        for entry in data["entry"]:
            for messaging in entry.get("messaging", []):
                if "message" in messaging:
                    sender_id = messaging["sender"]["id"]
                    message_text = messaging["message"].get("text", "")

                    # Respuesta automática
                    response = f"Recibí tu mensaje: {message_text}"

                    # Determinar si es Messenger o Instagram
                    if "instagram.com" in messaging["sender"].get("id", ""):
                        send_message(sender_id, response, ACCESS_TOKEN_INSTAGRAM)
                    else:
                        send_message(sender_id, response, ACCESS_TOKEN_MESSENGER)

    return "Evento recibido", 200

def send_message(user_id, text, access_token):
    """Enviar un mensaje de respuesta a Messenger o Instagram"""
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={access_token}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, data=json.dumps(payload), headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # Render usa el puerto 10000
