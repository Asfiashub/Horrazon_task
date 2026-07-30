import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from app.orchestrator import answer_question

load_dotenv()

app = Flask(__name__)
@app.route("/", methods=["GET"])
def home():
    return send_from_directory("static", "index.html")

AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "").strip()


def _check_auth(req):
    token = req.headers.get("Authorization", "").strip()
    return token == f"Bearer {AUTH_TOKEN}"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/query", methods=["POST"])
def query():
    if not _check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    question = data["question"]
    try:
        result = answer_question(question)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)