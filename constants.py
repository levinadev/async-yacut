import string
import re


# Константы для короткой ссылки (custom_id)
CUSTOM_ID_CHARACTERS = string.ascii_letters + string.digits
CUSTOM_ID_ALLOWED_PATTERN = re.compile(rf"^[{re.escape(CUSTOM_ID_CHARACTERS)}]+$")


CUSTOM_ID_RESERVED = ["files", "api", "admin"]
CUSTOM_ID_MIN_LENGTH = 1
CUSTOM_ID_MAX_LENGTH = 16
CUSTOM_ID_DEFAULT_LENGTH = 6