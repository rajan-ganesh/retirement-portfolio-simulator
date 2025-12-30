from flask import Blueprint, jsonify, request

from app.services.simulation_service import run_simulation

bp = Blueprint("main", __name__)


@bp.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="ok")


@bp.route("/api/simulate", methods=["POST"])
def simulate():
    payload = request.get_json(force=True, silent=False)

    try:
        result = run_simulation(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)
