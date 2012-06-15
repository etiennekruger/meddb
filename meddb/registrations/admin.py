from django.contrib import admin
import models

class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    fields = ('name', 'date')

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

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'medicine')

class MSHPriceAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'price')

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'contact_person', 'website', 'is_manufacturer')
    list_filter = ('country',)
    
    def contact_person(self, obj):
        return u'%s (%s)' % (obj.phone, obj.contact)

class SupplierInline(admin.StackedInline):
    model = models.Supplier
    max_num = 1
    extra = 1

class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website')
    list_filter = ('country',)
    inlines = (SupplierInline,)

class PackInline(admin.TabularInline):
    model = models.PackSize

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'product', 'manufacturer')
    inlines = (PackInline,)

class ProcurementAdmin(admin.ModelAdmin):
    pass

class ContextAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Country)
admin.site.register(models.Source, SourceAdmin)
admin.site.register(models.Incoterm, IncotermAdmin)
admin.site.register(models.DosageForm, DosageFormAdmin)
admin.site.register(models.INN, INNAdmin)
admin.site.register(models.Medicine, MedicineAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.MSHPrice, MSHPriceAdmin)
admin.site.register(models.Manufacturer, ManufacturerAdmin)
admin.site.register(models.Site)
admin.site.register(models.Supplier, SupplierAdmin)
admin.site.register(models.Pack)
admin.site.register(models.Registration, RegistrationAdmin)
admin.site.register(models.Procurement, ProcurementAdmin)
admin.site.register(models.Context, ContextAdmin)
