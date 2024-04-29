from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ScoreForm(FlaskForm):
    # title = StringField('Название')
    # content = TextAreaField("Содержание")
    # fullnames
    est_actual = StringField('Актуальность', validators=[DataRequired()])
    est_purpose = StringField('Цельность', validators=[DataRequired()])
    est_validity = StringField('Аргументированность', validators=[DataRequired()])
    est_resonance = StringField('Резонансность', validators=[DataRequired()])
    est_present_style = StringField('Точность и доходчивость языка')
    est_professionalism = StringField('Профессионально-этический подход', validators=[DataRequired()])
    est_feed_avail = StringField('Доступность подачи', validators=[DataRequired()])
    est_materials_cycle = StringField('Цикл материалов в различных жанрах', validators=[DataRequired()])
    est_add = StringField('Отрицательные баллы:\n\nрекламные материалы,', validators=[DataRequired()])
    est_cliche = StringField('Рекламные материалы', validators=[DataRequired()])
    est_contract = StringField('Материалы, носящие явно заказной характер', validators=[DataRequired()])
    est_gramm_errors = StringField('Грамматические ошибки', validators=[DataRequired()])
    est_lexical_errors = StringField('Нарушения орфоэпических, лексических норм', validators=[DataRequired()])

    # is_private = BooleanField("Личное")

    docx = FileField('docx')

    pdf = FileField('pdf')

    submit = SubmitField('Применить')
