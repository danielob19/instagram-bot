# app.py - Código del bot de Instagram con Flask

from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

# Variables de entorno (Render)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

@app.route('/webhook', methods=['GET'])
def verify():
    """Verifica el Webhook de Facebook"""
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if token_sent == VERIFY_TOKEN:
        return challenge
    return "Token inválido", 403

@app.route('/webhook', methods=['POST'])
def receive_message():
    """Recibe mensajes desde Instagram"""
    data = request.get_json()

    if data and "entry" in data:
        for entry in data["entry"]:
            for messaging in entry.get("messaging", []):
                if "message" in messaging:
                    sender_id = messaging["sender"]["id"]
                    message_text = messaging["message"].get("text", "")

                    # Generar respuesta automática
                    response = f"Recibí tu mensaje: {message_text}"

                    # Enviar mensaje de vuelta a Instagram
                    send_message(sender_id, response)

    return "Evento recibido", 200

def send_message(user_id, text):
    """Enviar un mensaje de respuesta en Instagram"""
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    # Debugging
    print(f"Mensaje enviado a {user_id}: {text}")
    print(f"Respuesta de Facebook: {response.status_code} - {response.text}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render usa un puerto dinámico
    app.run(host="0.0.0.0", port=port)
