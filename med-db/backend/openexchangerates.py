import requests
from main import app

API_BASE_URL = 'http://openexchangerates.org/api/'
OPEN_EXCHANGE_RATES_APP_ID = app.config['OPEN_EXCHANGE_RATES_APP_ID']


def call_api(self, endpoint):

        url = API_BASE_URL + endpoint + "?app_id=" + OPEN_EXCHANGE_RATES_APP_ID
        r = requests.get(url)
        r.raise_for_status()
        return r.json


class OpenExchangeRates(object):

    def convert_to_usd(self, currency, date=None):

        if not date:
            endpoint = 'latest.json'
            rates = call_api(endpoint)
        else:
            date_str = date.strftime('%Y-%m-%d')
            endpoint = 'historical/%s.json' % (date_str)
            rates = call_api(endpoint)
        return rates['rates'][currency]
    
    def get_currencies(self):
        endpoint = 'currencies.json'
        currencies = call_api(endpoint)
        return currencies
