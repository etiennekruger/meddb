import wtforms
from wtforms import Form
from wtforms import StringField, PasswordField, SelectField
from wtforms import validators
from flask.ext.babel import gettext


class LoginForm(Form):
    email = StringField('Email', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])

class ChangeLoginForm(Form):
    email = StringField('Email', [validators.InputRequired()])
    password = PasswordField('New password', [validators.InputRequired()])

available_countries = {
    "AGO":  gettext(u"Angola"),
    "BWA":  gettext(u"Botswana"),
    "COD":  gettext(u"DRC"),
    "LSO":  gettext(u"Lesotho"),
    "MDG":  gettext(u"Madagascar"),
    "MWI":  gettext(u"Malawi"),
    "MUS":  gettext(u"Mauritius"),
    "MOZ":  gettext(u"Mozambique"),
    "NAM":  gettext(u"Namibia"),
    "SYC":  gettext(u"Seychelles"),
    "ZAF":  gettext(u"South Africa"),
    "SWZ":  gettext(u"Swaziland"),
    "TZA":  gettext(u"Tanzania"),
    "ZMB":  gettext(u"Zambia"),
    "ZWE":  gettext(u"Zimbabwe"),
    }

country_choices = [(key, value) for key, value in available_countries.iteritems()]

class RegistrationForm(Form):
    email = StringField(gettext(u'Email Address'), [
        validators.Length(min=6, max=50),
        validators.Email(message=gettext(u"Please enter a valid email address."))
    ])
    password = PasswordField(gettext(u'Password'), [
        validators.Length(min=6, message=gettext(u"Your password needs to be at least 6 characters long.")),
        ])
    country = SelectField(gettext(u'Country'), [validators.InputRequired()], choices=country_choices)