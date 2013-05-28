from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
import models

# Widget from django tree features/select-filter. Some adjustments made.
class FilteredSelectSingle(forms.Select):
    """
    A Select with a JavaScript filter interface.
    """
    class Media:
        js = ("admin/js/fkfilter.js",)
        css = { 'all': ("admin/css/filteredselect.css",) }

    def __init__(self, verbose_name, attrs=None, choices=()):
        self.verbose_name = verbose_name
        super(FilteredSelectSingle, self).__init__(attrs, choices)

    def render(self, name, value, attrs={}, choices=()):
        attrs['class'] = 'selectfilter'
        output = [super(FilteredSelectSingle, self).render(
            name, value, attrs, choices)]
        output.append((
            '<script type="text/javascript">'
            'django.jQuery(document).ready(function(){'
            'django.jQuery("#id_%s").fk_filter("%s")'
            '});'
            '</script>'
        ) % (name, self.verbose_name.replace('"', '\\"'),));
        return mark_safe(u''.join(output))


#admin models
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'url')
    fields = ('name', 'date', 'url')

class IncotermAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class DosageFormAdmin(admin.ModelAdmin):
    list_display = ('name',)

class INNAdmin(admin.ModelAdmin):
    list_display = ('name',)

class IngredientInline(admin.TabularInline):
    model = models.Ingredient

class MedicineAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'dosageform')
    list_filter = ('dosageform',)
    inlines = (IngredientInline,)

class ProductAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        self.fields['manufacturer'].widget.widget = FilteredSelectSingle(verbose_name='manufacturers')
        self.fields['site'].widget.widget = FilteredSelectSingle(verbose_name='manufacturing sites')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'medicine', 'manufacturer')
    list_filter = ('manufacturer', 'medicine')
    form = ProductAdminForm

class MSHPriceAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'price')

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'contact_person', 'website', 'is_manufacturer')
    list_filter = ('country',)
    
    def contact_person(self, obj):
        return u'%s (%s)' % (obj.phone, obj.contact)

class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website')
    list_filter = ('country',)

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'product', 'manufacturer')

class ProcurementAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProcurementAdminForm, self).__init__(*args, **kwargs)
        self.fields['product'].widget.widget = FilteredSelectSingle(verbose_name='products')
        self.fields['supplier'].widget.widget = FilteredSelectSingle(verbose_name='suppliers')
        self.fields['container'].widget.widget = FilteredSelectSingle(verbose_name='container')

class ProcurementAdmin(admin.ModelAdmin):
    form = ProcurementAdminForm
    list_display = ('__unicode__', 'product', 'country')
    list_filter = ('country',)

class ContextAdmin(admin.ModelAdmin):
    pass

class SiteAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteAdminForm, self).__init__(*args, **kwargs)
        self.fields['manufacturer'].widget.widget = FilteredSelectSingle(verbose_name='manufacturers')

class SiteAdmin(admin.ModelAdmin):
    form = SiteAdminForm


admin.site.register(models.Country)
admin.site.register(models.Source, SourceAdmin)
admin.site.register(models.Incoterm, IncotermAdmin)
admin.site.register(models.DosageForm, DosageFormAdmin)
admin.site.register(models.INN, INNAdmin)
admin.site.register(models.Medicine, MedicineAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.MSHPrice, MSHPriceAdmin)
admin.site.register(models.Manufacturer, ManufacturerAdmin)
admin.site.register(models.Site, SiteAdmin)
admin.site.register(models.Supplier, SupplierAdmin)
admin.site.register(models.Container)
admin.site.register(models.Currency)
admin.site.register(models.Registration, RegistrationAdmin)
admin.site.register(models.Procurement, ProcurementAdmin)
admin.site.register(models.Context, ContextAdmin)
admin.site.register(models.Ingredient)
