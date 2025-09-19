from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import MultipleFileField, FileAllowed


class URLMapForm(FlaskForm):
    """
    Форма для главной страницы.
    """
    original_link = StringField(
        'Оригинальная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Сокращенная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 16)]
    )


class FileForm(FlaskForm):
    """
    Форма для страницы загрузки файлов.
    """
    files = MultipleFileField()
