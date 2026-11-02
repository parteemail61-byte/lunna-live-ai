from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
from threading import Lock

app = Flask(__name__)
CORS(app)

lock = Lock()

last_gift = {
    "event_id": 0,
    "gift": None,
    "reaction": None,
    "received_at": None
}

@app.route("/")
def home():
    return "LUNNA LIVE AI - Servidor online!"

@app.route("/health")
def health():
    return jsonify({"status": "online"})

@app.route("/gift")
def gift():
    with lock:
        return jsonify(last_gift)

@app.route("/test-gift", methods=["POST"])
def test_gift():
    global last_gift

    data = {
        "rose": ("Rosa", "rose"),
        "bouquet": ("Buquê", "bouquet"),
        "special": ("Presente especial", "special")
    }

    from flask import request
    reaction = request.args.get("reaction", "rose")

    if reaction not in data:
        return jsonify({"error": "Reação inválida"}), 400

    with lock:
        last_gift = {
            "event_id": last_gift["event_id"] + 1,
            "gift": data[reaction][0],
            "reaction": data[reaction][1],
            "received_at": datetime.now().isoformat()
        }

    return jsonify(last_gift)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
