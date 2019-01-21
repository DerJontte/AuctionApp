from datetime import datetime
from django.shortcuts import render
from django.views import View
from auctionApp.currency import Currency
from auctionApp.models import Auction


class BrowseAuctions(View):
    def get(self, request, **messages):
        request = assert_currency(request)
        currency = request.session['currency']
        if 'auctions' not in messages:
            auctions = Auction.objects.all().filter(active=True, banned=False, time_closing__gte=datetime.now()).order_by('time_closing')
        else:
            auctions = messages.get('auctions')

        for auction in auctions:
            auction.time_posted = auction.time_posted.strftime('%H:%M %d/%m/%y')
            auction.time_closing = auction.time_closing.strftime('%H:%M %d/%m/%y')
            if currency != 'EUR':
                converted_price = Currency.exchange(auction.current_price, currency)
                auction.current_price = "%.2f EUR (%.2f %s)" % (auction.current_price, converted_price, currency)
            else:
                auction.current_price = "%.2f EUR" % auction.current_price

        info_message = messages.get('info_message')
        error_message = messages.get('error_message')
        return render(request, 'browse.html', {'auctions': auctions,
                                               'info_message': info_message,
                                               'error_message': error_message, })

    def fetch_auction(request, number, **messages):
        request = assert_currency(request)
        auction = Auction.objects.get(id=number)
        if auction.banned and not request.user.is_superuser:
            return BrowseAuctions.get(None, request, error_message='The auction you tried to view has been banned')
        context = get_context(request, auction)

        ongoing = auction.time_closing.strftime('%Y%m%d%H%M%S') > datetime.now().strftime('%Y%m%d%H%M%S')

        auction.time_posted = auction.time_posted.strftime('%H:%M:%S %d/%m/%y')
        auction.time_closing = auction.time_closing.strftime('%H:%M:%S %d/%m/%y')

        info_message = messages.get('info_message')
        error_message = messages.get('error_message')
        return render(request, 'view_auction.html', {'auction': auction,
                                                          'currency': context['currency'],
                                                          'rate': context['rate'],
                                                          'starting_sum': context['starting_sum'],
                                                          'starting_price': context['starting_price'],
                                                          'current_price': context['current_price'],
                                                     'info_message': info_message,
                                                     'error_message': error_message,
                                                     'ongoing': ongoing})


def assert_currency(request):
    if not 'currency' in request.session:
        request.session['currency'] = 'EUR'
    if not 'currencies' in request.session:
        request.session['currencies'] = Currency.code_list()
    return request


def get_context(request, auction):
    currency = request.session['currency']
    if currency != 'EUR':
        rate = Currency.get_rate(currency)
        starting_converted = auction.starting_price * rate
        current_converted = auction.current_price * rate
        starting_sum = "%.2f" % starting_converted
        starting_price = "%.2f EUR (%s %s)" % (auction.starting_price, starting_sum, currency)
        current_price = "%.2f EUR (%.2f %s)" % (auction.current_price, current_converted, currency)
    else:
        starting_sum = None
        rate = 1
        starting_price = "%.2f EUR" % auction.starting_price
        current_price = "%.2f EUR" % auction.current_price

    return {'currency': currency, 'rate': rate, 'starting_sum': starting_sum, 'starting_price': starting_price, 'current_price': current_price}