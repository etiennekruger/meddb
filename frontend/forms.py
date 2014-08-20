import wtforms
from wtforms import Form
from wtforms import StringField, PasswordField, SelectField
from wtforms import validators


class LoginForm(Form):
    email = StringField('Email', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])

class ChangeLoginForm(Form):
    email = StringField('Email', [validators.InputRequired()])
    password = PasswordField('New password', [validators.InputRequired()])

available_countries = {
    "AGO":  "Angola",
    "BWA":  "Botswana",
    "COD":  "DRC",
    "LSO":  "Lesotho",
    "MDG":  "Madagascar",
    "MWI":  "Malawi",
    "MUS":  "Mauritius",
    "MOZ":  "Mozambique",
    "NAM":  "Namibia",
    "SYC":  "Seychelles",
    "ZAF":  "South Africa",
    "SWZ":  "Swaziland",
    "TZA":  "Tanzania",
    "ZMB":  "Zambia",
    "ZWE":  "Zimbabwe",
    }

available_titles = [
    "Mr",
    "Ms",
    "Mrs",
    "Dr",
    "Prof.",
]

country_choices = [(key, value) for key, value in available_countries.iteritems()]
title_choices = [(key, key) for key in available_titles]
title_choices += [("", "None"), ]

class RegistrationForm(Form):
    title = SelectField('Title', [], choices=title_choices)
    first_name = StringField('First Name', [validators.Required(message="Please enter your first name."), ])
    last_name = StringField('Last Name', [validators.Required(message="Please enter your last name."), ])
    email = StringField('Email Address', [
        validators.Length(min=6, max=50),
        validators.Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', [
        validators.Length(min=6, message="Your password needs to be at least 6 characters long."),
        ])
    country = SelectField('Country', [validators.InputRequired()], choices=country_choices)