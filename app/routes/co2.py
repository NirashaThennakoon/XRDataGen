from flask import Blueprint, request, jsonify, send_file
from dateutil import parser
from ..infra.plotting import line_png
from ..infra.scdm_client import SCDMClient
from ..infra.model_store import ModelStore
from ..services.prediction_service import PredictionService
from ..config import Config
from ..utils.time import local_now

bp = Blueprint("co2", __name__)

# Simple manual DI container for this blueprint
_cfg = Config()
_client = SCDMClient(_cfg.API_BASE, _cfg.API_EMAIL, _cfg.API_PASSWORD)
_store  = ModelStore(_cfg.SCALER_FILE, _cfg.LABEL_ENCODER_FILE, _cfg.MODEL_FILES)
_svc    = PredictionService(_client, _store, _cfg.SEQ_LEN, _cfg.PRED_HORIZON, _cfg.LOCAL_TZ)

@bp.route("/predict_co2", methods=["GET"])
def predict_co2():
    sensor_id = request.args.get("sensor_id")
    if not sensor_id:
        return jsonify({"error": "sensor_id is required"}), 400
    try:
        preds = _svc.predict_next(sensor_id)
        return jsonify({"predictions": preds})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/co2-graph", methods=["GET"])
def co2_graph():
    deviceui = request.args.get("deviceui")
    if not deviceui:
        return jsonify({"error": "deviceui is required"}), 400
    try:
        series = _svc.latest_series_for(deviceui, hours=6)
        if not series:
            return jsonify({"error": "No data found"}), 404
        times = [parser.isoparse(e["time"]) for e in series]
        values = [float(e["co2"]) for e in series]
        buf = line_png(times, values, f"CO₂ Levels - {deviceui}")
        return send_file(buf, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/co2", methods=["GET"])
def co2():
    deviceui = request.args.get("deviceui")
    if not deviceui:
        return jsonify({"error": "deviceui is required"}), 400
    try:
        series = _svc.latest_series_for(deviceui, hours=6)
        last = series[-6:]
        if not last:
            return jsonify({"error": "No data found"}), 404
        co2_values = [float(e["co2"]) for e in last]
        time_values = [parser.isoparse(e["time"]).astimezone().strftime("%H:%M") for e in last]
        return jsonify({"time_values": time_values, "co2_values": co2_values, "max_co2": max(co2_values)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
