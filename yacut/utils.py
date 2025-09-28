import random
import string


def get_unique_short_id(length=6):
    """Генерация случайного короткого идентификатора."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))
