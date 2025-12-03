from flask import Flask, request, jsonify
from datetime import datetime
import random

app = Flask(__name__)

@app.route("/echo_unstable", methods=["POST"])
def echo_unstable():
    # 20% simulated failure
    if random.random() < 0.2:
        return "Simulated server failure", 500

    data = request.get_data()
    size = len(data)
    ts = datetime.utcnow().isoformat() + "Z"
    return jsonify({
        "payload": data.decode("utf-8", errors="ignore"),
        "size_bytes": size,
        "timestamp": ts
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)