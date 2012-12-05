from django.db import models
from django.conf import settings

from openexchangerates import OpenExchangeRates

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % (self.code)
    
    class Meta:
        verbose_name_plural = 'Currencies'

class ExchangeRateManager(models.Manager):
    _app_id = getattr(settings, 'OPENEXCHANGERATES_APP_ID', None)
    _rates = OpenExchangeRates(_app_id)

    def _get_currency(self, **kwargs):
        currency = kwargs.get('currency', None)
        if currency:
            return currency
        currency_id = kwargs.get('currency__id', None)
        if currency_id:
            currency = Currency.objects.get(pk=currency_id)
            return currency
        currency_id = kwargs.get('currency_id', None)
        if currency_id:
            currency = Currency.objects.get(pk=currency_id)
            return currency
        currency_code = kwargs.get('currency__code', None)
        if currency_code:
            currency = Currency.objects.get(code=currency_code.upper())
            return currency
    
    def _create_exchangerate(self, **kwargs):
        try:
            currency = self._get_currency(**kwargs)
        except:
            raise ExchangeRate.DoesNotExist
        date = kwargs.get('date', None)
        obj = ExchangeRate()
        obj.currency = currency
        obj.date = date
        try:
            obj.rate = self._rates.get(currency.code, date)
        except Exception, e:
            print e
            raise ExchangeRate.DoesNotExist
        if date:
            obj.save()
        return obj
    
    def get(self, *args, **kwargs):
        date = kwargs.get('date', None)
        if not date:
            return self._create_exchangerate(**kwargs)
        try:
            obj = super(ExchangeRateManager, self).get(*args, **kwargs)
            return obj
        except ExchangeRate.DoesNotExist:
            return self._create_exchangerate(**kwargs)

class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency)
    rate = models.FloatField()
    date = models.DateField()
    
    objects = ExchangeRateManager()
    
    def __unicode__(self):
        if self.date:
            return u'1 %s = %.4f USD on %s' % (self.currency.code,
                                               self.rate,
                                               self.date.isoformat())
        else:
            return u'1 %s = %.4f USD' % (self.currency.code,
                                         self.rate)            

