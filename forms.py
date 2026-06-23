from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, FloatField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
import re

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно'),
        Length(min=2, max=80, message='Имя должно быть от 2 до 80 символов')
    ])
    email = EmailField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    confirm_password = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен')
    ])


class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно'),
        Length(min=2, max=80, message='Имя должно быть от 2 до 80 символов')
    ])
    email = EmailField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email')
    ])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(),
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    confirm_password = PasswordField('Подтверждение пароля', validators=[
        DataRequired(),
        EqualTo('new_password', message='Пароли не совпадают')
    ])


class TransactionForm(FlaskForm):
    amount = FloatField('Сумма', validators=[
        DataRequired(message='Введите сумму'),
        NumberRange(min=0.01, message='Сумма должна быть больше 0')
    ])
    category = SelectField('Категория', choices=[
        ('food', 'Продукты'),
        ('transport', 'Транспорт'),
        ('home', 'Жилье'),
        ('entertainment', 'Развлечения'),
        ('health', 'Здоровье'),
        ('education', 'Образование'),
        ('salary', 'Зарплата'),
        ('freelance', 'Фриланс'),
        ('investment', 'Инвестиции'),
        ('gift', 'Подарки'),
        ('bonus', 'Премия'),
        ('business', 'Бизнес'),
        ('other', 'Другое')
    ], validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[Length(max=200)])
    date = DateField('Дата', validators=[DataRequired()])
    type = SelectField('Тип', choices=[
        ('expense', 'Расход'),
        ('income', 'Доход')
    ], validators=[DataRequired()])