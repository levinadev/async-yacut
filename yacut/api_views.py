from flask import jsonify, request

from . import app, db
from .models import URLMap
from .utils import get_unique_short_id

from constants import (
    CUSTOM_ID_ALLOWED_PATTERN,
)

@app.route("/api/id/", methods=["POST"])
def create_short_link():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Отсутствует тело запроса"}), 400

    if "url" not in data:
        return jsonify({"message": '"url" является обязательным полем!'}), 400

    original = data["url"]
    custom_id = data.get("custom_id")

    if custom_id:
        if len(custom_id) > 16 or not CUSTOM_ID_ALLOWED_PATTERN.match(custom_id):
            return (
                jsonify({"message": "Указано недопустимое "
                                    "имя для короткой ссылки"}),
                400,
            )
    else:
        custom_id = get_unique_short_id()

    if URLMap.query.filter_by(short=custom_id).first():
        return (
            jsonify(
                {"message": "Предложенный вариант "
                            "короткой ссылки уже существует."}
            ),
            400,
        )

    urlmap = URLMap(original=original, short=custom_id)
    db.session.add(urlmap)
    db.session.commit()

    short_link = request.host_url.rstrip("/") + "/" + custom_id
    return jsonify({"url": original, "short_link": short_link}), 201


@app.route("/api/id/<string:short_id>/", methods=["GET"])
def get_original_url(short_id):
    urlmap = URLMap.query.filter_by(short=short_id).first()

    if not urlmap:
        return jsonify({"message": "Указанный id не найден"}), 404

    return jsonify({"url": urlmap.original})
