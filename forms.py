from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    FieldList,
    FormField,
    SubmitField,
    FileField,
)
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    text = StringField("Question Text", validators=[DataRequired()])
    option1 = StringField("Option 1", validators=[DataRequired()])
    option2 = StringField("Option 2", validators=[DataRequired()])
    option3 = StringField("Option 3", validators=[DataRequired()])
    option4 = StringField("Option 4", validators=[DataRequired()])
    correct_option = StringField("Correct Option", validators=[DataRequired()])


class CreateQuizForm(FlaskForm):
    title = StringField("Quiz Title", validators=[DataRequired()])
    description = TextAreaField("Quiz Description")
    questions = FieldList(FormField(QuestionForm), min_entries=1)
    submit = SubmitField("Create Quiz")


class UploadQuizForm(FlaskForm):
    file = FileField("Upload CSV File", validators=[DataRequired()])
    submit = SubmitField("Upload Quiz")
