from http import HTTPStatus

from flask import jsonify, render_template

from . import app


@app.errorhandler(HTTPStatus.NOT_FOUND)
def not_found_error(error):
    if "/api/" in str(error):
        return (jsonify({"message": "Ресурс не найден"}),
                HTTPStatus.NOT_FOUND)
    return (
        render_template(
            "404.html",
            error_code=HTTPStatus.NOT_FOUND,
            message="Страница не найдена",
        ),
        HTTPStatus.NOT_FOUND,
    )


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    if "/api/" in str(error):
        return (jsonify({"message": "Внутренняя ошибка сервера"}),
                HTTPStatus.INTERNAL_SERVER_ERROR)
    return (
        render_template(
            "500.html",
            error_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Ошибка на сервере"
        ),
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )
