import random

from constants import (
    CUSTOM_ID_DEFAULT_LENGTH,
    CUSTOM_ID_CHARACTERS
)


def get_unique_short_id(length=CUSTOM_ID_DEFAULT_LENGTH):
    """Генерация случайного короткого идентификатора."""
    return "".join(random.choices(CUSTOM_ID_CHARACTERS, k=length))
