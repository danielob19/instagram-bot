# app.py - Bot de Instagram y Messenger conectado al asistente de la web

from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Cargar variables de entorno desde Render
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN_MESSENGER = os.getenv("ACCESS_TOKEN_MESSENGER")
ACCESS_TOKEN_INSTAGRAM = os.getenv("ACCESS_TOKEN_INSTAGRAM")
WEB_ASSISTANT_URL = "https://licbustamante.com.ar/api/asistente"  # URL del asistente de la web

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
    """Recibe mensajes desde Messenger e Instagram y los reenvía al asistente web"""
    data = request.get_json()

    if "entry" in data:
        for entry in data["entry"]:
            for messaging in entry.get("messaging", []):
                if "message" in messaging:
                    sender_id = messaging["sender"]["id"]
                    message_text = messaging["message"].get("text", "")

                    # Enviar el mensaje al asistente de la web y recibir la respuesta
                    ai_response = get_assistant_response(message_text)

                    # Detectar si es Instagram o Messenger
                    if "ig_id" in messaging["sender"]:
                        send_instagram_message(sender_id, ai_response)
                    else:
                        send_messenger_message(sender_id, ai_response)

    return "Evento recibido", 200

def get_assistant_response(text):
    """Consulta el asistente web y obtiene la respuesta"""
    try:
        payload = {"message": text}
        headers = {"Content-Type": "application/json"}
        response = requests.post(WEB_ASSISTANT_URL, data=json.dumps(payload), headers=headers)
        response_data = response.json()
        return response_data.get("reply", "No pude procesar tu mensaje.")
    except Exception as e:
        return f"Error al conectar con el asistente: {str(e)}"

def send_messenger_message(user_id, text):
    """Enviar un mensaje a Messenger"""
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={ACCESS_TOKEN_MESSENGER}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, data=json.dumps(payload), headers=headers)

def send_instagram_message(user_id, text):
    """Enviar un mensaje a Instagram"""
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={ACCESS_TOKEN_INSTAGRAM}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, data=json.dumps(payload), headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
