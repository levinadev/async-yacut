import asyncio
import os

import aiohttp
from dotenv import load_dotenv
from flask import Flask

from yacut.utils import get_unique_short_id

load_dotenv()

API_HOST = os.environ.get("API_HOST")
API_VERSION = os.environ.get("API_VERSION")
DISK_TOKEN = os.environ.get("DISK_TOKEN")

AUTH_HEADERS = {"Authorization": f"OAuth {DISK_TOKEN}"}

UPLOAD_URL = f"{API_HOST}{API_VERSION}/disk/resources/upload"
DOWNLOAD_URL = f"{API_HOST}{API_VERSION}/disk/resources/download"

app = Flask(__name__)


async def upload_file_and_get_url(session, file):
    """Загрузить один файл на Яндекс.Диск
    и вернуть короткую ссылку + прямую ссылку"""
    path = f"app:/{file.filename}"

    async with session.get(
        UPLOAD_URL,
        headers=AUTH_HEADERS,
        params={"path": path, "overwrite": "true"},
    ) as resp:
        data = await resp.json()
        upload_href = data["href"]

    async with session.put(upload_href, data=file.read()) as resp:
        if resp.status not in (201, 202):
            raise Exception(
                f"Ошибка загрузки файла {file.filename}, статус {resp.status}"
            )

    async with session.get(
        DOWNLOAD_URL, headers=AUTH_HEADERS, params={"path": path}
    ) as resp:
        data = await resp.json()
        direct_url = data["href"]

    short_id = get_unique_short_id()
    return {"filename": file.filename, "short_id": short_id, "url": direct_url}


async def async_upload_files_to_yandex(files):
    """Асинхронная загрузка списка файлов на Яндекс."""
    if files:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for f in files:
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_and_get_url(session, f)))
            results = await asyncio.gather(*tasks)

        return results
    return []
