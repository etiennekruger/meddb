import urllib2
import json

from datetime import datetime, timedelta

API_BASE_URL = 'http://openexchangerates.org/api'

class OpenExchangeRates(object):
    _cache = {}
    
    def __init__(self, app_id):
        self.app_id = app_id
    
    def _prune_cache(self):
        #TODO: Maybe limit number of entries in cache. The way it is now will
        # eat memory and become slow for situations with *many* queries per day.
        # Should be fine for our current requirements though.
        for url, data in self._cache.items():
            if (datetime.now() - data['time']) > timedelta(days=1):
                del self._cache[url]
    
    def _loadurl(self, url):
        self._prune_cache()
        cached = self._cache.get(url, None)
        if cached:
            return cached['data']
        url = '%s/%s?app_id=%s' % (API_BASE_URL, url, self.app_id)
        print url
        response = urllib2.urlopen(url)
        data = json.load(response)
        self._cache[url] = { 'data': data,
                             'time': datetime.now() }
        return data

    def get(self, currency, date=None):
        if not date:
            url = 'latest.json'
            rates = self._loadurl(url)
            return rates['rates'][currency]
        else:
            date_str = date.strftime('%Y-%m-%d')
            url = 'historical/%s.json' % (date_str)
            rates = self._loadurl(url)
            return rates['rates'][currency]
    
    def get_currencies(self):
        url = 'currencies.json'
        currencies = self._loadurl(url)
        return currencies
