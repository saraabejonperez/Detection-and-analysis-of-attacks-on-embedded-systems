from flask import Blueprint, jsonify
import time

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "model_loaded": False,
        "detecting": False,
        "device_time": int(time.time())
    })