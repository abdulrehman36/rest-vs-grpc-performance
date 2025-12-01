from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(force=True) or {}
    payload = data.get("payload", "")
    size_bytes = len(payload.encode("utf-8"))

    return jsonify({
        "payload": payload,
        "size_bytes": size_bytes,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)