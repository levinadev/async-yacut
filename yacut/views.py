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
    Обрабатывает загрузку файлов пользователем.

    GET-запрос: отображает страницу upload.html с формой для загрузки файлов.
    POST-запрос:
        1. Получает файлы из формы (input name="files").
        2. Создаёт event loop и запускает асинхронную функцию async_upload_files_to_yandex.
        3. Сохраняет короткие ссылки в базу данных.
        4. Отображает страницу с уже загруженными файлами и всеми ссылками из базы.
    """
    results_to_display = []

    if request.method == 'POST':
        print("[INFO] Получен POST-запрос на /files")
        files = request.files.getlist("files")
        print(f"[DEBUG] Количество файлов: {len(files)}")
        for f in files:
            print(f"[DEBUG] Имя файла: {f.filename}")

        # создаём новый event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("[INFO] Event loop создан и установлен")

        # асинхронная загрузка файлов на Яндекс
        results = loop.run_until_complete(async_upload_files_to_yandex(files))
        print(f"[INFO] Загрузка завершена. Результаты: {results}")
        loop.close()
        print("[INFO] Event loop закрыт")

        # сохраняем результаты в базу
        for r in results:
            # проверяем уникальность short_id
            while URLMap.query.filter_by(short=r['short_id']).first():
                r['short_id'] = get_unique_short_id()

            urlmap = URLMap(original=r['url'], short=r['short_id'])
            db.session.add(urlmap)
            db.session.commit()

            # добавляем в список для отображения
            results_to_display.append({
                "filename": r['filename'],
                "short_url": url_for('follow_link', short=r['short_id'], _external=False)
            })

    # GET-запрос или после POST показываем страницу с результатами
    all_links = URLMap.query.order_by(URLMap.timestamp.desc()).all()

    return render_template('upload.html', results=results_to_display, all_links=all_links)
