# YaCut
Проект YaCut — это сервис укорачивания ссылок. Его назначение — ассоциировать длинную пользовательскую ссылку с короткой, которую предлагает сам пользователь или предоставляет сервис.
Дополнительная функция YaCut — загрузка сразу нескольких файлов на Яндекс Диск и предоставление коротких ссылок пользователю для скачивания этих файлов.


### Как запустить проект Yacut:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone 
```

```
cd yacut
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать в директории проекта файл .env с четыремя переменными окружения:

```
FLASK_APP=yacut
FLASK_DEBUG=1
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URI=sqlite:///db.sqlite3
DISK_TOKEN=y0__xDN_96sBxjWrzogouqTuBSC4j3rvDDBhWWEoMBG7Bbl1i82tw
API_HOST=https://cloud-api.yandex.net/
API_VERSION=v1
```

Создать базу данных и применить миграции:

```
flask db upgrade
```

Запустить проект:

```
flask run
```


### Примеры запросов
-  Создание короткой ссылки
POST /api/id/

Тело запроса:
```
{
  "url": "https://example.com/some/long/url"
}
```

Пример ответа:
```
{
  "short_link": "http://127.0.0.1/AbCdEf",
  "url": "https://example.com/some/long/url"
}
```

- Получение оригинальной ссылки
GET /api/id/<short_id>/

Пример запроса:
```
GET http://127.0.0.1/api/id/myLink123/
```

Пример ответа:
```
{
  "url": "https://example.com/some/long/url"
}
```

### Используемые технологии
- Python 3.10
- Flask — веб-фреймворк
- SQLAlchemy — ORM для работы с БД
- Alembic — миграции базы данных
- aiohttp — асинхронные запросы к API Яндекс.Диска
- pytest — тестирование
- dotenv — работа с переменными окружения

### Автор
- Имя: Анна
- Email: anna45dd@yandex.ru
- GitHub: https://github.com/levinadev


