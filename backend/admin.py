from backend import logger, app, db
import models
from flask import Flask, flash, redirect, url_for, request, render_template, g
from flask.ext.admin import Admin, expose, AdminIndexView, helpers
from flask.ext.admin.form import rules
from flask.ext.admin.model.template import macro
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.sqla.filters import FilterEqual
from wtforms import form, fields, validators, BooleanField
from datetime import datetime
import urllib

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

    form_args = dict(
        cv_url={'label': 'Link to CV (e.g. Linked-In profile)'},
        technical_forecasting={'label': 'Forecasting/quantification'},
        technical_planning={'label': 'Procurement planning'},
        technical_logistics={'label': 'Procurement (technical aspects)'},
        technical_handling={'label': 'Clearing and handling'},
        technical_inventory={'label': 'Warehouse management (Inventory control)'},
        technical_distribution={'label': 'Distribution and transport'},
        technical_information_systems={'label': 'Information systems for the above'},
        technical_monitoring={'label': 'Monitoring and evaluation'},
        technical_training={'label': 'Training in the above'},
        regional_east_africa={'label': 'Eastern Africa & Indian Ocean'},
        regional_west_central_africa={'label': 'West and Central Africa'},
        regional_southern_africa={'label': 'Southern Africa'},
        regional_north_africa={'label': 'Middle East and North Africa'},
        regional_eastern_europe={'label': 'Eastern Europe and Central Asia'},
        regional_south_asia={'label': 'South and West Asia'},
        regional_east_asia={'label': 'East Asia and the Pacific'},
        regional_latin_america={'label': 'Latin America and the Caribbean'},
        language_english={'label': 'English'},
        language_french={'label': 'French'},
        language_spanish={'label': 'Spanish'},
        language_portuguese={'label': 'Portuguese'},
        language_russian={'label': 'Russian'},
    )

    form_edit_rules = (
        'email',
        'country',
        'cv_url',
        rules.FieldSet([
                           'technical_forecasting',
                           'technical_planning',
                           'technical_logistics',
                           'technical_handling',
                           'technical_inventory',
                           'technical_distribution',
                           'technical_information_systems',
                           'technical_monitoring',
                           'technical_training',
                           ],
                       header='Technical experience'
        ),
        rules.FieldSet([
                           'regional_east_africa',
                           'regional_west_central_africa',
                           'regional_southern_africa',
                           'regional_north_africa',
                           'regional_eastern_europe',
                           'regional_south_asia',
                           'regional_east_asia',
                           'regional_latin_america',
                           ],
                       header='Regional experience'
        ),
        rules.FieldSet([
                           'language_english',
                           'language_french',
                           'language_spanish',
                           'language_portuguese',
                           'language_russian',
                           ],
                       header='Language proficiency'
        ),
    )


class ProcurementView(MyModelView):
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
    form_excluded_columns = [
        # 'country',
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
        ('container', models.Procurement.container),
        ('pack_price_usd', models.Procurement.pack_price_usd),
        ('quantity', models.Procurement.quantity),
        ('source', models.Source.name),
        ('approved', models.Procurement.approved),
        ('supplier', models.Supplier.name),
        ]

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.country_id = g.user.country.country_id if g.user.country else None
            model.added_by = g.user

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True):
        # Todo: add some custom logic here?
        count, query = super(ProcurementView, self).get_list(page, sort_column, sort_desc, search, filters, execute=False)
        query = query.all()
        return count, query


class MedicineView(MyRestrictedModelView):
    column_default_sort = 'name'
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
        ]

    def after_model_change(self, form, model, is_created):
        if is_created:
            model.added_by = g.user


# Index view
class HomeView(AdminIndexView):

    @expose('/')
    def index(self):
        return self.render('admin/home.html')



admin = Admin(app, name='Medicine Prices Database', base_template='admin/my_master.html', index_view=HomeView(name='Home'), subdomain='med-db-api')

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

admin.add_view(ProcurementView(models.Procurement, db.session, name="Procurements", endpoint='procurement'))