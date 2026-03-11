from flask import Blueprint, jsonify
from datetime import datetime
import pytz

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "model_loaded": False,
        "detecting": False,
        "device_time": datetime.now(pytz.timezone('Europe/Madrid')).strftime("%d-%m-%Y %H:%M:%S")
    })