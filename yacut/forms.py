from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Optional

from constants import (
    CUSTOM_ID_MIN_LENGTH,
    CUSTOM_ID_MAX_LENGTH
)


class URLMapForm(FlaskForm):
    """Форма для главной страницы."""

    original_link = StringField(
        "Оригинальная ссылка",
        validators=[DataRequired(message="Обязательное поле")],
    )
    custom_id = StringField(
        "Сокращенная ссылка",
        validators=[
            Optional(),
            Length(CUSTOM_ID_MIN_LENGTH, CUSTOM_ID_MAX_LENGTH)
        ]
    )


class FileForm(FlaskForm):
    """Форма для страницы загрузки файлов."""

    files = MultipleFileField()
