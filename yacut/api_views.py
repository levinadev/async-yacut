from flask import Flask, request, jsonify
from . import app, db
from .models import URLMap
from .utils import get_unique_short_id


@app.route("/api/id/", methods=["POST"])
def create_short_url():
    """
    POST /api/id/
    body JSON: {"url": "длинная ссылка", "custom_id": "опционально короткий id"}

    return JSON: {"url": "<длинная ссылка>", "short_url": "<короткая ссылка>"}
    """
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "URL не указан"}), 400

    original = data["url"]
    custom_id = data.get("custom_id")

    if not custom_id:
        custom_id = get_unique_short_id()

    if URLMap.query.filter_by(short=custom_id).first():
        return jsonify({"error": "Короткий идентификатор уже занят"}), 409

    urlmap = URLMap(original=original, short=custom_id)
    db.session.add(urlmap)
    db.session.commit()

    short_url = request.host_url.rstrip("/") + "/api/id/" + custom_id
    return jsonify({"url": original, "short_url": short_url}), 201


@app.route("/api/id/<string:short_id>/", methods=["GET"])
def get_original_url(short_id):
    """
    GET /api/id/<short_id>/

    return JSON: {"url": "<длинная ссылка>"}
    """
    urlmap = URLMap.query.filter_by(short=short_id).first()
    if not urlmap:
        return jsonify({"error": "Короткая ссылка не найдена"}), 404

    return jsonify({"url": urlmap.original})
