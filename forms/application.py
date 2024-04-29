from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ProjectsForm(FlaskForm):
    # title = StringField('Название')
    # content = TextAreaField("Содержание")
    # fullnames
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    # information
    post = StringField('Должность')
    place = StringField('Место работы')
    topic = StringField('Тема работы', validators=[DataRequired()])
    heading = StringField('Заголовок работы', validators=[DataRequired()])
    annotation = TextAreaField('Аннотация', validators=[DataRequired()])

    # is_private = BooleanField("Личное")

    docx = FileField('docx')

    pdf = FileField('pdf')

    submit = SubmitField('Применить')
