import aiohttp
import asyncio
import os
from pprint import pprint
import urllib
import requests
from dotenv import load_dotenv

load_dotenv()
API_HOST = os.environ.get('API_HOST')
API_VERSION = os.environ.get('API_VERSION')
DISK_TOKEN = os.environ.get('DISK_TOKEN')


# ---- запросить информацию о Диске ----

DISK_INFO_URL = f'{API_HOST}{API_VERSION}/disk/'

# Словарь с заголовком авторизации.
# AUTH_HEADERS = {
#     'Authorization': f'OAuth {DISK_TOKEN}'
# }
#
# # Запрос.
# response = requests.get(url=DISK_INFO_URL, headers=AUTH_HEADERS)
# pprint(response.json())

# ------------------------------------------

#  -- загрузить файл на Яндекс Диск ---
#     Запросить GET-запросом URL для загрузки файла.
#     Загрузить файл PUT-запросом по предоставленному URL.

REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'

AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}

payload = {
    # Загрузить файл с названием filename.txt в папку приложения.
    'path': f'app:/filename.txt',
    'overwrite': 'True'  # Если файл существует, перезаписать его.
}
response = requests.get(
    headers=AUTH_HEADERS,  # Заголовок для авторизации.
    params=payload,  # Указать параметры.
    url=REQUEST_UPLOAD_URL
)

upload_url = response.json()['href']
print(upload_url)

# --- Загрузка файла на Диск через полученный URL ---

with open('filename.txt', 'rb') as file:
    response = requests.put(
        data=file,
        url=upload_url,
    )

# Расположение файла находится в заголовке Location.
location = response.headers['Location']
# Декодировать строку при помощи модуля urllib.
location = urllib.parse.unquote(location)
# Убрать первую часть расположения файла /disk,
# она не понадобится.
location = location.replace('/disk', '')
print(location)

# -------------------------------------

# -- получить ссылку на скачивание файла с Яндекс Диска ---
# -------------------------------------
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

load_dotenv()
DISK_TOKEN = os.environ.get('DISK_TOKEN')

AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}

response = requests.get(
    headers=AUTH_HEADERS,
    url=DOWNLOAD_LINK_URL,
    params={'path': '/Приложения/Uploader/filename.txt'}
)

link = response.json()['href']
print(link) # Ссылка на скачивание файла


# асинхронная загрузка файлов на Яндекс Диск с собственной генерацией коротких ссылок для каждого файла.

async def async_upload_files_to_dropbox(images):
    if images is not None:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for image in images:
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_and_get_url(session, image)
                    )
                )
            urls = await asyncio.gather(*tasks)
        return urls


async def upload_file_and_get_url(session, image):
    dropbox_args = json.dumps({
        'autorename': True,
        'mode': 'add',
        'path': f'/{image.filename}',
    })
    async with session.post(
            UPLOAD_LINK,
            headers={
                'Authorization': AUTH_HEADERS,
                'Content-Type': 'application/octet-stream',
                'Dropbox-API-Arg': dropbox_args
            },
            data=image.read()
    ) as response:
        data = await response.json()
        path = data['path_lower']
    async with session.post(
            SHARING_LINK,
            headers={
                'Authorization': AUTH_HEADERS,
                'Content-Type': 'application/json',
            },
            json={'path': path}
    ) as response:
        data = await response.json()
        if 'url' not in data:
            data = data['error']['shared_link_already_exists']['metadata']
        url = data['url']
        url = url.replace('&dl=0', '&raw=1')
    return url