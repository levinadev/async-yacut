import asyncio
import re

from flask import redirect, render_template, request, url_for

from . import app, db
from .models import URLMap
from .utils import get_unique_short_id
from .yandex import async_upload_files_to_yandex

ALLOWED_CUSTOM_ID = re.compile(r"^[A-Za-z0-9]+$")
RESERVED_SHORTS = ["files", "api", "admin"]


@app.route("/", methods=["GET", "POST"])
def index():
    """Главная страница."""
    if request.method == "POST":
        original = request.form.get("original_link")
        custom_id = request.form.get("custom_id")

        if not original:
            return render_template("index.html", error="Укажите длинную ссылку.")

        if custom_id:
            if len(custom_id) > 16:
                return render_template(
                    "index.html",
                    error=("Длина короткой ссылки не должна " "превышать 16 символов."),
                )
            if not ALLOWED_CUSTOM_ID.match(custom_id):
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
            custom_id in RESERVED_SHORTS
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
