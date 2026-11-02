from flask import Flask, jsonify
from threading import Thread
import os

app = Flask(__name__)

last_gift = {
    "gift": None,
    "reaction": None
}

@app.route("/")
def home():
    return "LUNNA LIVE AI - Servidor online!"

@app.route("/gift")
def gift():
    return jsonify(last_gift)

@app.route("/health")
def health():
    return jsonify({"status": "online"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
