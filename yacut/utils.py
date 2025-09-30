import random
import string

DEFAULT_SHORT_ID_LENGTH = 6
SHORT_ID_CHARACTERS = string.ascii_letters + string.digits

def get_unique_short_id(length=DEFAULT_SHORT_ID_LENGTH):
    """Генерация случайного короткого идентификатора."""
    return "".join(random.choices(SHORT_ID_CHARACTERS, k=length))
