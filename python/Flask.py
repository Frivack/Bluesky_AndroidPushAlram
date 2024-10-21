# flask_app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

# 토큰 저장소 (메모리상에 임시로 저장)
tokens = []

@app.route('/register_token', methods=['POST'])
def register_token():
    data = request.get_json()
    token = data.get('token')
    if token:
        tokens.append(token)
        return jsonify({"message": "Token received"}), 200
    return jsonify({"error": "Invalid data"}), 400

@app.route('/tokens', methods=['GET'])
def get_tokens():
    return jsonify({"tokens": tokens}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
