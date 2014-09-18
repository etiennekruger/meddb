from backend import logger, app, db
import models
from flask import Flask, flash, redirect, url_for, request, render_template, g, abort
from flask.ext.admin import Admin, expose, BaseView, AdminIndexView, helpers
from flask.ext.admin.model.template import macro
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.sqla.filters import FilterEqual
from flask.ext.admin.helpers import get_redirect_target
from wtforms import form, fields, validators, BooleanField
from datetime import datetime
import urllib
import forms

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


class MyModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = False
    page_size = app.config['RESULTS_PER_PAGE']
    list_template = "admin/custom_list_template.html"
    column_exclude_list = []

    def is_accessible(self):
        if g.user is not None:
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            return redirect(HOST + 'login/?next=' + urllib.quote_plus(request.url), code=302)


class MyRestrictedModelView(MyModelView):

    def is_accessible(self):
        if g.user is not None and g.user.is_admin:
            return True
        return False


class UserView(MyRestrictedModelView):
    can_create = False
    column_list = ['country', 'email', 'is_admin', 'activated']
    column_exclude_list = ['password_hash']
    form_excluded_columns = [
        'password_hash',
        'procurements_added',
        'procurements_approved',
        'manufacturers_added',
        'manufacturers_approved',
        'suppliers_added',
        'suppliers_approved',
        'products_added',
        'products_approved',
        ]


class ProcurementView(MyModelView):
    list_template = 'admin/procurement_list_template.html'
    column_list = [
        'country',
        'medicine',
        'pack_size',
        'container',
        'pack_price_usd',
        'quantity',
        'supplier',
        'manufacturer',
        'date',
        'source',
        'approved'
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
        ('container', models.Procurement.container),
        ('pack_price_usd', models.Procurement.pack_price_usd),
        ('quantity', models.Procurement.quantity),
        ('source', models.Source.name),
        ('approved', models.Procurement.approved),
        ('supplier', models.Supplier.name),
        ]

    def populate_procurement_from_form(self, procurement, form):
        # manually assign form values to procurement object
        procurement.country_id = form.country.data
        procurement.currency_id = form.currency.data
        procurement.product_id = form.product.data
        procurement.supplier_id = form.supplier.data
        procurement.container = form.container.data
        procurement.pack_size = form.pack_size.data
        procurement.pack_price = form.pack_price.data
        procurement.pack_price_usd = form.pack_price_usd.data
        procurement.unit_price_usd = form.unit_price_usd.data
        procurement.quantity = form.quantity.data
        procurement.method = form.method.data
        procurement.start_date = form.start_date.data
        procurement.end_date = form.end_date.data
        return procurement

    @expose('/new/', methods=('GET', 'POST'))
    def add_view(self):
        form = forms.ProcurementForm(request.form)
        if request.method == 'POST' and form.validate():
            procurement = models.Procurement()
            procurement.added_by = g.user
            procurement = self.populate_procurement_from_form(procurement, form)
            db.session.add(procurement)
            db.session.commit()
            flash("The details were updated successfully.", "success")
        if g.user.country:
            form.country.process_data(g.user.country.country_id)
        return self.render('admin/procurement.html', form=form, title="Add procurement record")

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if (not request.args) or (not request.args.get('id')):
            return abort(404)
        id = request.args['id']
        procurement = models.Procurement.query.get(id)
        form = forms.ProcurementForm(request.form, procurement)
        if request.form:
            # update procurement details
            if request.method == 'POST' and form.validate():
                procurement = self.populate_procurement_from_form(procurement, form)
                db.session.add(procurement)
                db.session.commit()
                flash("The details were updated successfully.", "success")
                if request.args.get('host_url'):
                    target = get_redirect_target(param_name="host_url")
                    return redirect(HOST + target)
        else:
            # set field values that weren't picked up automatically
            form.product.process_data(procurement.product_id)
            form.country.process_data(procurement.country_id)
            form.currency.process_data(procurement.currency_id)
            form.incoterm.process_data(procurement.incoterm_id)
            form.supplier.process_data(procurement.supplier_id)
        return self.render('admin/procurement.html', procurement=procurement, form=form, title="Edit procurement record")


class MedicineView(MyRestrictedModelView):
    column_default_sort = ('name', models.Medicine.name)
    column_searchable_list = [
        'name',
        ]
    column_list = [
        'name',
        'dosage_form',
        'unit_of_measure',
        ]
    column_sortable_list = [
        ('name', models.Medicine.name),
        ('dosage_form', models.DosageForm.name),
        ('unit_of_measure', models.UnitOfMeasure.value),
        ]
    form_excluded_columns = [
        'benchmarks',
        'products',
        ]


class BenchmarkView(MyRestrictedModelView):
    column_list = [
        'medicine',
        'name',
        'year',
        'price',
        ]
    column_sortable_list = [
        ('medicine', models.Medicine.name),
        ('name', models.BenchmarkPrice.name),
        ('price', models.BenchmarkPrice.price),
        ('year', models.BenchmarkPrice.year),
        ]
    form_excluded_columns = [
        'unit_of_measure',
        ]


class ManufacturerView(MyModelView):
    column_searchable_list = [
        'name',
        ]
    column_exclude_list = [
        'added_by',
        ]
    form_excluded_columns = [
        'added_by',
        ]
    column_sortable_list = [
        ('country', models.Country.name),
        ]
    column_searchable_list = [
        'name',
        ]
    column_formatters = dict(
        country=macro('render_country'),
        )

    def after_model_change(self, form, model, is_created):
        if is_created:
            model.added_by = g.user


class SupplierView(MyModelView):
    column_searchable_list = [
        'name',
        ]
    column_list = [
        'name',
        'street_address',
        'website',
        'contact',
        ]
    column_sortable_list = [
        ('name', models.Supplier.name),
        ('contact', models.Supplier.contact),
        ('street_address', models.Supplier.street_address),
        ('website', models.Supplier.website),
        ]
    form_excluded_columns = [
        'added_by',
        'authorized',
        'procurements',
        ]
    column_searchable_list = [
        'name',
        'street_address',
        'website',
        'contact',
        ]

    def after_model_change(self, form, model, is_created):
        if is_created:
            model.added_by = g.user


class ProductView(MyModelView):

    column_list = [
        'medicine',
        'description',
        'manufacturer',
        'site',
        'is_generic',
        ]

    column_exclude_list = [
        'added_by',
        'average_price',
        ]

    column_sortable_list = [
        ('medicine', models.Medicine.name),
        ('manufacturer', models.Manufacturer.name),
        ]

    form_excluded_columns = [
        'added_by',
        'procurements',
        'average_price',
        'shelf_life',
        'registrations',
        ]

    def after_model_change(self, form, model, is_created):
        if is_created:
            model.added_by = g.user


# Index view
class HomeView(AdminIndexView):

    @expose('/')
    def index(self):
        return self.render('admin/home.html')


admin = Admin(app, name='Medicine Prices Database', base_template='admin/my_master.html', index_view=HomeView(name='Home'), subdomain='med-db-api', template_mode='bootstrap3')

admin.add_view(UserView(models.User, db.session, name="Users", endpoint='user'))

admin.add_view(MyRestrictedModelView(models.DosageForm, db.session, name="Dosage Forms", endpoint='dosage_form', category='Medicines'))
admin.add_view(MedicineView(models.Medicine, db.session, name="Available Medicines", endpoint='medicine', category='Medicines'))
admin.add_view(BenchmarkView(models.BenchmarkPrice, db.session, name="Benchmark Prices", endpoint='benchmark_price', category='Medicines'))

admin.add_view(MyRestrictedModelView(models.Incoterm, db.session, name="Incoterms", endpoint='incoterm', category='Form Options'))
admin.add_view(MyRestrictedModelView(models.UnitOfMeasure, db.session, name="Unit of Measure", endpoint='uom', category='Form Options'))
admin.add_view(MyRestrictedModelView(models.AvailableContainers, db.session, name="Containers", endpoint='container', category='Form Options'))
admin.add_view(MyRestrictedModelView(models.AvailableProcurementMethods, db.session, name="Procurement Methods", endpoint='procurement_method', category='Form Options'))

admin.add_view(ManufacturerView(models.Manufacturer, db.session, name="Manufacturer", endpoint='manufacturer', category='Manufacturers/Suppliers'))
admin.add_view(MyModelView(models.Site, db.session, name="Site", endpoint='site', category='Manufacturers/Suppliers'))
admin.add_view(ProductView(models.Product, db.session, name="Product", endpoint='product', category='Manufacturers/Suppliers'))
admin.add_view(SupplierView(models.Supplier, db.session, name="Supplier", endpoint='supplier', category='Manufacturers/Suppliers'))

admin.add_view(ProcurementView(models.Procurement, db.session, name="Procurement", endpoint='procurement'))
