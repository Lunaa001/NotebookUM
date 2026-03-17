from flask import Blueprint, jsonify, request
from ..services.ai_service import AIService

ai_bp = Blueprint("ai", __name__)
ai_service = AIService()


@ai_bp.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    prompt = data.get("prompt", "")
    response = ai_service.query(prompt)
    return jsonify({"response": response})
