from flask import Flask, jsonify
from flask_cors import CORS
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent, ConnectEvent
from threading import Thread, Lock
from datetime import datetime
import time
import os

app = Flask(__name__)
CORS(app)

USERNAME = "@lunnamoraes_sf"
lock = Lock()

last_gift = {
    "event_id": 0,
    "gift": None,
    "reaction": None,
    "received_at": None
}

connection = {
    "status": "aguardando",
    "message": "Aguardando a LIVE começar"
}

def save_gift(name, reaction):
    global last_gift
    with lock:
        last_gift = {
            "event_id": last_gift["event_id"] + 1,
            "gift": name,
            "reaction": reaction,
            "received_at": datetime.now().isoformat()
        }

def gift_reaction(name):
    normalized = name.lower()

    if "rose" in normalized or "rosa" in normalized:
        return "rose"

    if "bouquet" in normalized or "buquê" in normalized or "buque" in normalized:
        return "bouquet"

    return "special"

def listen_tiktok():
    while True:
        try:
            connection["status"] = "conectando"
            connection["message"] = "Conectando à LIVE..."

            client = TikTokLiveClient(unique_id=USERNAME)

            @client.on(ConnectEvent)
            async def on_connect(event):
                connection["status"] = "online"
                connection["message"] = "Conectado à LIVE da Lunna!"
                print("Conectado à LIVE!")

            @client.on(GiftEvent)
            async def on_gift(event):
                gift = event.gift
                if gift is None:
                    return

                if event.streaking:
                    return

                name = gift.name or "Presente"
                reaction = gift_reaction(name)

                save_gift(name, reaction)
                print(f"Presente recebido: {name} -> {reaction}")

            client.run()

        except Exception as error:
            connection["status"] = "aguardando"
            connection["message"] = str(error)
            print("TikTok desconectado:", error)

        time.sleep(20)

@app.route("/")
def home():
    return "LUNNA LIVE AI - Servidor online!"

@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "tiktok": connection["status"],
        "message": connection["message"]
    })

@app.route("/gift")
def gift():
    with lock:
        return jsonify(last_gift)

@app.route("/test-gift", methods=["POST"])
def test_gift():
    reaction = "rose"
    save_gift("Teste", reaction)
    return jsonify(last_gift)

if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not os.environ.get("WERKZEUG_RUN_MAIN"):
    Thread(target=listen_tiktok, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
