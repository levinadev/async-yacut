# YaCut

![CI/CD](https://github.com/levinadev/async-yacut/actions/workflows/main.yml/badge.svg)

Проект YaCut — это сервис укорачивания ссылок. Его назначение — ассоциировать длинную пользовательскую ссылку с короткой, которую предлагает сам пользователь или предоставляет сервис.
Дополнительная функция YaCut — загрузка сразу нескольких файлов на Яндекс Диск и предоставление коротких ссылок пользователю для скачивания этих файлов.

### Демо
- [Развернутый проект](https://yacut.levinadev.ru/)


### Запуск через Docker

1. Создать файл `.env` из примера:

```
cp .env.example .env
```

2. Запустить контейнеры:

```
docker compose -f docker-compose.production.yml up -d --build
```

3. Приложение будет доступно по адресу:

```
http://localhost:8011
```

Остановка:

```
docker compose -f docker-compose.production.yml down
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


