"""Routes for summaries API endpoints"""

from flask import Blueprint, jsonify

from app.services.summary_service import SummaryService

summaries_bp = Blueprint("summaries", __name__, url_prefix="/api/v1/summaries")
summary_service = SummaryService()


@summaries_bp.route("/document/<int:document_id>", methods=["GET"])
def get_document_summary(document_id: int):
    try:
        summary = summary_service.get_by_id(document_id)
        return jsonify({"success": True, "data": summary}), 200
    except ValueError as exc:
        return (
            jsonify(
                {
                    "success": False,
                    "message": str(exc),
                    "documento_id": document_id,
                }
            ),
            404,
        )