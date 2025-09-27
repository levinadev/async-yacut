import os
import aiohttp
import asyncio
import urllib.parse
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for
from yacut.utils import get_unique_short_id

load_dotenv()

API_HOST = os.environ.get('API_HOST')
API_VERSION = os.environ.get('API_VERSION')
DISK_TOKEN = os.environ.get('DISK_TOKEN')

AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}

UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

app = Flask(__name__)


# -------------------------------
# Асинхронная загрузка на Яндекс Диск
# -------------------------------
async def upload_file_and_get_url(session, file):
    """Загрузить один файл на Яндекс.Диск и вернуть короткую ссылку + прямую ссылку"""
    path = f'app:/{file.filename}'

    # 1. Получаем upload_href
    async with session.get(
        UPLOAD_URL,
        headers=AUTH_HEADERS,
        params={'path': path, 'overwrite': 'true'}
    ) as resp:
        data = await resp.json()
        upload_href = data['href']

    # 2. Загружаем содержимое файла
    async with session.put(upload_href, data=file.read()) as resp:
        if resp.status not in (201, 202):
            raise Exception(f"Ошибка загрузки файла {file.filename}, статус {resp.status}")

    # 3. Получаем прямую ссылку
    async with session.get(
        DOWNLOAD_URL,
        headers=AUTH_HEADERS,
        params={'path': path}
    ) as resp:
        data = await resp.json()
        direct_url = data['href']

    # 4. Генерируем короткий id
    short_id = get_unique_short_id()
    return {"filename": file.filename, "short_id": short_id, "url": direct_url}


async def async_upload_files_to_yandex(files):
    """
    Асинхронная загрузка списка файлов на Яндекс.

    Args:
        files (list): Список файлов (например, из Flask request.files.getlist).

    Returns:
        list: Список результатов загрузки (обычно — URL'ы файлов на Яндексе).
              Если список файлов пуст, вернётся пустой список.
    """
    if files:
        print(f"[🌷 INFO] Начинаем загрузку {len(files)} файлов")

        tasks = []

        # создаём асинхронную сессию для HTTP-запросов (одна на все файлы)
        async with aiohttp.ClientSession() as session:
            print("[🌷 INFO] Создана aiohttp-сессия")

            for f in files:
                print(f"[🌷 DEBUG] Создаём задачу для файла: {f.filename}")
                # для каждого файла создаём задачу: загрузить и получить ссылку
                tasks.append(asyncio.ensure_future(upload_file_and_get_url(session, f)))

            # запускаем все задачи параллельно и ждём завершения
            print("[🌷 INFO] Запускаем асинхронные задачи...")
            results = await asyncio.gather(*tasks)
            print("[🌷 INFO] Все задачи завершены")

        # возвращаем список результатов (например, ссылок)
        print(f"[🌷 RESULT] Получены результаты: {results}")
        return results
    print("[🌷 WARN] Список файлов пуст, возвращаем []")
    return []

async def main():
    async with aiohttp.ClientSession() as session:
        result = await upload_file_and_get_url(session, "anna.txt")
        print("Результат:", result)


if __name__ == '__main__':
    asyncio.run(main())