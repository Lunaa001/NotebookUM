"""Users API routes"""

from flask import Blueprint, request, jsonify
from app.services.user_service import UserService

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")
user_service = UserService()


@users_bp.post("")
def create_user():
    """Create a new user"""
    data = request.get_json() or {}

    try:
        user = user_service.create(data)

        response = jsonify(user.to_dict())
        response.status_code = 201
        return response
    except AttributeError:
        response = jsonify(user)
        response.status_code = 201
        return response
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@users_bp.get("/<int:user_id>")
def get_user(user_id: int):
    """Retrieve a user by ID"""
    try:
        user = user_service.get_by_id(user_id)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 404

    try:
        payload = user.to_dict()
    except AttributeError:
        payload = user

    response = jsonify(payload)
    response.status_code = 200
    return response
