import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    API_HOST = os.getenv('API_HOST', 'https://cloud-api.yandex.net')
    API_VERSION = os.getenv('API_VERSION', '/v1')
