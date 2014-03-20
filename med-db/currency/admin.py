from django.contrib import admin
from models import Currency, ExchangeRate

class ExchangeRateAdmin(admin.ModelAdmin):
    list_filter = ('currency',)
    list_display = ('currency', 'rate', 'date')

admin.site.register(Currency)
admin.site.register(ExchangeRate, ExchangeRateAdmin)
