from flask import render_template, request, redirect, url_for
from . import app
import asyncio
from flask import render_template, request, redirect, url_for, flash
from . import app, db
from .models import URLMap
from .utils import get_unique_short_id
from .yandex import async_upload_files_to_yandex


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Главная страница приложения (сокращатель ссылок).

    GET → возвращает форму для ввода длинной ссылки и (опционально) короткого идентификатора.
    POST → принимает данные формы:
        - Проверяет, что длинная ссылка указана.
        - Генерирует короткий идентификатор, если пользователь его не задал.
        - Проверяет, что идентификатор ещё не занят.
        - Сохраняет пару (original, short) в базе данных.
        - Возвращает ту же страницу с готовой короткой ссылкой.
    """
    if request.method == "POST":
        original = request.form.get("original_link")
        custom_id = request.form.get("custom_id")

        print(f"Длинная ссылка, от клиента: {original}")
        print(f"Короткая ссылка (опционально), от клиента: {custom_id}")

        if not original:
            return render_template("index.html", error="Укажите длинную ссылку.")

        # если пользователь не ввёл свой идентификатор → генерируем
        if not custom_id:
            custom_id = get_unique_short_id()
            print(f"Сгенерированный короткий идентификатор: {custom_id}")

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
    """
    Обработчик перехода по короткой ссылке.

    - Принимает короткий идентификатор из URL.
    - Ищет его в базе данных.
    - Если запись найдена → выполняет redirect на оригинальную (длинную) ссылку.
    - Если запись не найдена → автоматически возвращает 404.
    """
    print(f"Пришёл короткий идентификатор из URL: {short}")
    urlmap = URLMap.query.filter_by(short=short).first_or_404()
    print(f"Нашли в БД: original={urlmap.original}, short={urlmap.short}")
    return redirect(urlmap.original)


@app.route('/files', methods=['GET', 'POST'])
def upload_file():
    """
    Загрузка файлов и генерация коротких ссылок на них.

    - GET: просто отображаем форму загрузки.
    - POST: обрабатываем загруженные файлы, создаём короткие ссылки, отображаем результаты.
    """
    if request.method == 'POST':
        results_to_display = []

        files = request.files.getlist("files")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(async_upload_files_to_yandex(files))
        loop.close()

        for r in results:
            # генерируем уникальный short_id
            while URLMap.query.filter_by(short=r['short_id']).first():
                r['short_id'] = get_unique_short_id()

            # сохраняем в базу
            urlmap = URLMap(original=r['url'], short=r['short_id'])
            db.session.add(urlmap)
            db.session.commit()

            # добавляем в список для отображения
            results_to_display.append({
                "filename": r['filename'],
                "short_url": url_for('follow_link', short=r['short_id'], _external=True)
            })

        # POST → возвращаем страницу с результатами
        return render_template('upload.html', results=results_to_display)

    # GET → просто форма, результатов пока нет
    return render_template('upload.html')


