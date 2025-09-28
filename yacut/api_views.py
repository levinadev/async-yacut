from flask import Flask, request, jsonify
from . import app, db
from .models import URLMap
from .utils import get_unique_short_id
import re

ALLOWED_CUSTOM_ID = re.compile(r'^[A-Za-z0-9]+$')


@app.route("/api/id/", methods=["POST"])
def create_short_link():
    """
    POST /api/id/
    body JSON: {"url": "длинная ссылка", "custom_id": "опционально короткий id"}

    return JSON: {"url": "<длинная ссылка>", "short_link": "<короткая ссылка>"}
    """
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"message": "\"url\" является обязательным полем!"}), 400

    original = data["url"]
    custom_id = data.get("custom_id")

    if custom_id:
        if not ALLOWED_CUSTOM_ID.match(custom_id):
            return jsonify({"message": "Указано недопустимое имя для короткой ссылки."}), 400
    else:
        custom_id = get_unique_short_id()

    if URLMap.query.filter_by(short=custom_id).first():
        return jsonify({"message": "Предложенный вариант короткой ссылки уже существует."}), 400

    urlmap = URLMap(original=original, short=custom_id)
    db.session.add(urlmap)
    db.session.commit()

    short_link = request.host_url.rstrip("/") + "/" + custom_id
    return jsonify({"url": original, "short_link": short_link}), 201


@app.route("/api/id/<string:short_id>/", methods=["GET"])
def get_original_url(short_id):
    """
    GET /api/id/<short_id>/

    return JSON: {"url": "<длинная ссылка>"}
    """
    urlmap = URLMap.query.filter_by(short=short_id).first()
    if not urlmap:
        return jsonify({"error": "Короткая ссылка не найдена."}), 404

    return jsonify({"url": urlmap.original})
