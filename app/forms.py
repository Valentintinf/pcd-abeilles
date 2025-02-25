from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisteur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("S'inscrire")


class RegistrationForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    password2 = PasswordField(
        "confirmer Password", validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField("S'inscrire")

    def validate_username(self, username):
        print(username.data)
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        print(user)
        if user is not None:
            raise ValidationError("Utiliser un autre nom d'utilisateur.")

    def validate_email(self, email):
        print(email.data)
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        print(user)
        if user is not None:
            raise ValidationError('Utiliser un autre email')
