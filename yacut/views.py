import asyncio

from flask import redirect, render_template, request, url_for

from constants import (
    CUSTOM_ID_MAX_LENGTH,
    CUSTOM_ID_ALLOWED_PATTERN,
    CUSTOM_ID_RESERVED,
)
from . import app, db
from .models import URLMap
from .utils import get_unique_short_id
from .yandex import async_upload_files_to_yandex


@app.route("/", methods=["GET", "POST"])
def index():
    """Главная страница."""
    if request.method == "POST":
        original = request.form.get("original_link")
        custom_id = request.form.get("custom_id")

        if not original:
            return render_template(
                "index.html",
                error="Укажите длинную ссылку.",
            )

        if custom_id:
            if len(custom_id) > CUSTOM_ID_MAX_LENGTH:
                return render_template(
                    "index.html",
                    error=(
                        f"Длина короткой ссылки не "
                        f"должна превышать {CUSTOM_ID_MAX_LENGTH} символов."
                    ),
                )
            if not CUSTOM_ID_ALLOWED_PATTERN.match(custom_id):
                return render_template(
                    "index.html",
                    error=(
                        "Короткая ссылка может содержать только "
                        "латинские буквы и цифры."
                    ),
                )
        else:
            custom_id = get_unique_short_id()

        if (
                custom_id in CUSTOM_ID_RESERVED
                or URLMap.query.filter_by(short=custom_id).first()
        ):
            return render_template(
                "index.html",
                error=("Предложенный вариант короткой ссылки уже существует."),
            )

        urlmap = URLMap(original=original, short=custom_id)
        db.session.add(urlmap)
        db.session.commit()

        short_url = url_for("follow_link", short=custom_id, _external=True)
        return render_template("index.html", short_url=short_url)

    return render_template("index.html")


@app.route("/<string:short>")
def follow_link(short):
    """Переход по короткой ссылке."""
    urlmap = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(urlmap.original)


@app.route("/files", methods=["GET", "POST"])
def upload_file():
    """
    Загрузка файлов на Яндекс.Диск
    и создание коротких ссылок.
    """
    if request.method == "POST":

        results_to_display = []

        files = request.files.getlist("files")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(async_upload_files_to_yandex(files))
        loop.close()

        for r in results:
            while URLMap.query.filter_by(short=r["short_id"]).first():
                r["short_id"] = get_unique_short_id()

            urlmap = URLMap(original=r["url"], short=r["short_id"])
            db.session.add(urlmap)
            db.session.commit()

            results_to_display.append(
                {
                    "filename": r["filename"],
                    "short_url": url_for(
                        "follow_link", short=r["short_id"], _external=True
                    ),
                }
            )

        return render_template("upload.html", results=results_to_display)

    return render_template("upload.html")
