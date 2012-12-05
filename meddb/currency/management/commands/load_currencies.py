from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from currency import models
from currency.openexchangerates import OpenExchangeRates

class Command(BaseCommand):
    def handle(self, *args, **options):
        app_id = getattr(settings, 'OPENEXCHANGERATES_APP_ID', None)
        rates = OpenExchangeRates(app_id)
        currencies = rates.get_currencies()
        
        with transaction.commit_on_success():
            for code, description in currencies.items():
                obj, created = models.Currency.objects.get_or_create(code=code)
                obj.description = description
                obj.save()
                if created:
                    print 'Created new currency: %s' % (obj.code)
