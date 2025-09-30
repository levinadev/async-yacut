import asyncio
import aiohttp
from http import HTTPStatus
from settings import Config
from yacut.utils import get_unique_short_id

AUTH_HEADERS = {"Authorization": f"OAuth {Config.DISK_TOKEN}"}
UPLOAD_URL = f"{Config.API_HOST}{Config.API_VERSION}/disk/resources/upload"
DOWNLOAD_URL = f"{Config.API_HOST}{Config.API_VERSION}/disk/resources/download"


async def upload_file_and_get_url(session, file):
    """Загрузка файла на Яндекс.Диск"""
    path = f"app:/{file.filename}"

    async with session.get(
            UPLOAD_URL,
            headers=AUTH_HEADERS,
            params={"path": path, "overwrite": "true"},
    ) as resp:
        data = await resp.json()
        upload_href = data["href"]

    async with session.put(upload_href, data=file.read()) as resp:
        if resp.status not in (HTTPStatus.CREATED, HTTPStatus.ACCEPTED):
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
