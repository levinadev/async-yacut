from flask import render_template, request, redirect, url_for
from . import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist("files")
        for f in files:
            print("Загружен файл:", f.filename)
        return redirect(url_for('success'))
    return render_template('upload.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error_code=404, message="Страница не найдена"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html', error_code=500, message="Ошибка сервера"), 500
