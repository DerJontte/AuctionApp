from urllib import request
from auctionApp.models import ExchangeRate
import json, datetime, pytz


# TODO: städa upp koden
class Currency:
    def assert_currency(request):
        if 'currency' not in request.session:
            request.session['currency'] = 'EUR'
        if 'currencies' not in request.session:
            request.session['currencies'] = Currency.code_list()

    def exchange(input, code):
        return round(input * Currency.get_rate(code), 2)

    def get_rate(code):
        if ExchangeRate.objects.get(code=code).last_updated < datetime.datetime.now().replace(tzinfo=pytz.UTC)- datetime.timedelta(hours=24):
            Currency.fetch_rates()
        return ExchangeRate.objects.get(code=code).rate

    def code_list(**type):
        if ExchangeRate.objects.count() == 0:
            Currency.fetch_rates()
        keylist = []
        for key in ExchangeRate.objects.all():
            if type.get('type') == 'pairlist':
                keylist.append([key.code, key.code])
            else:
                keylist.append(key.code)
        return keylist

    def fetch_rates(*self):
        url = 'http://data.fixer.io/api/latest?access_key=5833765f3462250964a319f06fd6b3d1&format=1'
        response = request.urlopen(url)
        data = response.read()
        parsed = json.loads(data)
        for rate in parsed['rates'].items():
                tosave = ExchangeRate(code=rate[0], rate=rate[1])
                tosave.save()
