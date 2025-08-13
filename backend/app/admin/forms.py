from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    """登入表單"""
    username = StringField('使用者名稱', validators=[DataRequired()])
    password = PasswordField('密碼', validators=[DataRequired()])
    remember = BooleanField('記住我')
    submit = SubmitField('登入')