import wtforms
from wtforms import Form
from wtforms import StringField, PasswordField, SelectField
from wtforms import validators


class LoginForm(Form):
    email = StringField('Email', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])

country_choices = [
    ("BWA", "Botswana"),
    ("MWI", "Malawi"),
    ("SYC", "Seychelles"),
    ("ZAF", "South Africa"),
    ("TZA", "Tanzania"),
    ("ZMB", "Zambia"),
    ]

class RegistrationForm(Form):
    email = StringField('Email Address', [
        validators.Length(min=6, max=50),
        validators.Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', [
        validators.Length(min=6, message="Your password needs to be at least 6 characters long."),
        ])
    country = SelectField('Country', [validators.InputRequired()], choices=country_choices)