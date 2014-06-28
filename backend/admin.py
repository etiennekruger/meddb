from backend import logger, app, db
import models
from flask import Flask, flash, redirect, url_for, request, render_template
from flask.ext.admin import Admin, expose, AdminIndexView, helpers
from flask.ext.admin.model.template import macro
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext import login
from wtforms import form, fields, validators, BooleanField
from datetime import datetime

HOST = app.config['HOST']

@app.context_processor
def inject_paths():
    return dict(HOST=HOST)

@app.template_filter('add_commas')
def jinja2_filter_add_commas(quantity):
    out = ""
    quantity_str = str(quantity)
    while len(quantity_str) > 3:
        tmp = quantity_str[-3::]
        out = "," + tmp + out
        quantity_str = quantity_str[0:-3]
    return quantity_str + out


country_choices = [
    ("BWA", "Botswana"),
    ("MWI", "Malawi"),
    ("SYC", "Seychelles"),
    ("ZAF", "South Africa"),
    ("TZA", "Tanzania"),
    ("ZMB", "Zambia"),
]

# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    email = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != hash(self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(models.User).filter_by(email=self.email.data).first()


class RegistrationForm(form.Form):
    email = fields.TextField(validators=[validators.required(), validators.email()])
    password = fields.PasswordField(
        validators=[
            validators.required(),
            validators.length(min=6, message="Your password needs to have at least six characters.")
        ]
    )
    country = fields.SelectField(choices=country_choices)

    def validate_login(self, field):
        if db.session.query(models.User).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError('Duplicate users')


class MyModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    page_size = app.config['RESULTS_PER_PAGE']
    list_template = "admin/custom_list_template.html"
    column_exclude_list = []

    def is_accessible(self):
        return login.current_user.is_authenticated()


class MyRestrictedModelView(MyModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_admin


class UserView(MyModelView):
    can_create = False
    column_list = ['country', 'email', 'is_admin', 'activated']
    column_exclude_list = ['password']
    form_excluded_columns = ['password', 'procurements_added', 'procurements_approved']

    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_admin


class ProcurementView(MyModelView):
    column_list = [
        'country',
        'medicine',
        'pack_size',
        'unit_of_measure',
        'container',
        'pack_price_usd',
        'quantity',
        'supplier',
        'manufacturer',
        'date',
        'source',
        'approved'
    ]
    form_excluded_columns = [
        'country',
        'approved_by',
        'added_by',
        'added_on',
        ]
    column_formatters = dict(
        country=macro('render_country'),
        medicine=macro('render_procurement_medicine'),
        manufacturer=macro('render_procurement_manufacturer'),
        pack_price_usd=macro('render_price'),
        start_date=macro('render_date'),
        quantity=macro('render_quantity'),
        date=macro('render_procurement_date'),
        approved=macro('render_approve'),
    )
    column_sortable_list = [
        ('country', models.Country.name),
        ('medicine', models.Medicine.name),
        ('pack_size', models.Procurement.pack_size),
        ('unit_of_measure', models.Procurement.unit_of_measure),
        ('container', models.Procurement.container),
        ('pack_price_usd', models.Procurement.pack_price_usd),
        ('quantity', models.Procurement.quantity),
        ('source', models.Source.name),
        ('approved', models.Procurement.approved),
        ('supplier', models.Supplier.name),
        ]

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.country_id = login.current_user.country.country_id if login.current_user.country else None
            model.added_by = login.current_user

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True):
        # Todo: add some custom logic here?
        count, query = super(ProcurementView, self).get_list(page, sort_column, sort_desc, search, filters, execute=False)
        query = query.all()
        return count, query


class MedicineView(MyRestrictedModelView):
    column_list = [
        'name',
        'dosage_form',
    ]
    column_sortable_list = [
        'name',
        ('dosage_form', models.DosageForm.name),
        ]
    form_excluded_columns = [
        'benchmarks',
        'products',
        'added_by',
        ]

    def after_model_change(self, form, model, is_created):
        if is_created:
            model.added_by = login.current_user


class ManufacturerView(MyModelView):
    column_exclude_list = [
        'added_by',
        ]
    form_excluded_columns = [
        'added_by',
        ]

    def after_model_change(self, form, model, is_created):
        if is_created:
            model.added_by = login.current_user


# Customized index view that handles login & registration
class HomeView(AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return self.render('admin/home.html')
        # return render_template('admin/home.html')

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            if user:
                if not user.is_active():
                    flash('Your account has not been activated. Please contact the site administrator.' , 'error')
                    return redirect(url_for('.login_view'))
                else:
                    login.login_user(user)
            else:
                flash('Username or Password is invalid' , 'error')
                return redirect(url_for('.login_view'))

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'

        return self.render('admin/home.html', form=form, link=link)

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = models.User()

            # hash password, before populating User object
            form.password.data = hash(form.password.data)
            country = models.Country.query.filter(models.Country.code==form.country.data).first()
            form.country.data =country
            form.populate_obj(user)

            # activate the admin user
            if user.email == app.config['ADMIN_USER']:
                user.is_admin = True
                user.activated = True

            db.session.add(user)
            db.session.commit()

            flash('Please wait for your new account to be activated.', 'info')
            return redirect(url_for('.login_view'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to sign in.</a></p>'
        return self.render('admin/home.html', form=form, link=link, register=True)

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = ".login_view"

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(models.User).get(user_id)

init_login()

admin = Admin(app, name='Medicine Prices Database', base_template='admin/my_master.html', index_view=HomeView(name='Home'))

admin.add_view(UserView(models.User, db.session, name="Users", endpoint='user'))

admin.add_view(MyRestrictedModelView(models.DosageForm, db.session, name="Dosage Forms", endpoint='dosage_form', category='Medicines'))
admin.add_view(MyRestrictedModelView(models.Ingredient, db.session, name="Medicine Components", endpoint='ingredient', category='Medicines'))
admin.add_view(MedicineView(models.Medicine, db.session, name="Available Medicines", endpoint='medicine', category='Medicines'))
admin.add_view(MyRestrictedModelView(models.BenchmarkPrice, db.session, name="Benchmark Prices", endpoint='benchmark_price', category='Medicines'))

admin.add_view(MyRestrictedModelView(models.Incoterm, db.session, name="Incoterms", endpoint='incoterm', category='Form Options'))
admin.add_view(MyRestrictedModelView(models.AvailableContainers, db.session, name="Containers", endpoint='container', category='Form Options'))
admin.add_view(MyRestrictedModelView(models.AvailableUnits, db.session, name="Units of Measure", endpoint='units', category='Form Options'))
admin.add_view(MyRestrictedModelView(models.AvailableProcurementMethods, db.session, name="Procurement Methods", endpoint='procurement_method', category='Form Options'))

admin.add_view(ManufacturerView(models.Manufacturer, db.session, name="Manufacturer", endpoint='manufacturer'))
admin.add_view(MyModelView(models.Supplier, db.session, name="Supplier", endpoint='supplier'))
admin.add_view(ProcurementView(models.Procurement, db.session, name="Procurements", endpoint='procurement'))