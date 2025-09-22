from flask import render_template, request, redirect, url_for
from . import app

from flask import render_template, request, redirect, url_for, flash
from . import app, db
from .models import URLMap
from .utils import get_unique_short_id

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original = request.form.get("original_link")
        custom_id = request.form.get("custom_id")

        if not original:
            return render_template("index.html", error="Укажите длинную ссылку.")

        # если пользователь не ввёл свой идентификатор → генерируем
        if not custom_id:
            custom_id = get_unique_short_id()

        # проверим, не занят ли идентификатор
        if URLMap.query.filter_by(short=custom_id).first():
            return render_template("index.html", error="Предложенный вариант короткой ссылки уже существует.")

        # создаём и сохраняем в БД
        urlmap = URLMap(original=original, short=custom_id)
        db.session.add(urlmap)
        db.session.commit()

        short_url = url_for("follow_link", short=custom_id, _external=True)
        return render_template("index.html", short_url=short_url)

    return render_template("index.html")


@app.route("/<string:short>")
def follow_link(short):
    urlmap = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(urlmap.original)



@app.route('/files', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist("files")
        for f in files:
            print("Загружен файл:", f.filename)
        return redirect(url_for('success'))
    return render_template('upload.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error_code=404, message="Страница не найдена"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html', error_code=500, message="Ошибка сервера"), 500
