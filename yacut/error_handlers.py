from flask import jsonify, render_template

from . import app


@app.errorhandler(404)
def not_found_error(error):
    if "/api/" in str(error):
        return jsonify({"message": "Ресурс не найден"}), 404
    return (
        render_template(
            "404.html",
            error_code=404,
            message="Страница не найдена",
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    if "/api/" in str(error):
        return jsonify({"message": "Внутренняя ошибка сервера"}), 500
    return (
        render_template(
            "500.html",
            error_code=500,
            message="Ошибка на сервере"
        ),
        500,
    )
