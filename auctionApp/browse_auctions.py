from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime
from auctionApp.currency import Currency
from auctionApp.models import Auction


class Auctions(View):
    def get(self, request):
        Currency.assert_currency(request)
        currency = request.session['currency']

        auctions = Auction.objects.all().filter(active=True, banned=False, time_closing__gte=datetime.now()).order_by('time_closing')

        if 'search_query' in request.session:
            auctions = auctions.filter(title__contains=request.session['search_query'])
            del request.session['search_query']

        for auction in auctions:
            auction.time_closing = auction.time_closing.strftime('%d/%m/%y %H:%M')
            if currency != 'EUR':
                converted_price = Currency.exchange(auction.current_price, currency)
                auction.current_price = "%.2f EUR (%.2f %s)" % (auction.current_price, converted_price, currency)
            else:
                auction.current_price = "%.2f EUR" % auction.current_price

        return render(request, 'home.html', {'auctions': auctions})

    def fetch_auction(request, number):
        auction = Auction.objects.get(id=number)
        if auction.banned and not request.user.is_superuser:
            request.error_message = 'The auction you tried to view has been banned'
            return redirect('home')
        context = get_context(request, auction)

        auction.time_posted = auction.time_posted.strftime('%d/%m/%y %H:%M')
        auction.time_closing = auction.time_closing.strftime('%d/%m/%y %H:%M')

        return render(request, 'view_auction.html', {'auction': auction,
                                                     'currency': context['currency'],
                                                     'rate': context['rate'],
                                                     'starting_sum': context['starting_sum'],
                                                     'starting_price': context['starting_price'],
                                                     'current_price': context['current_price']})


def get_context(request, auction):
    Currency.assert_currency(request)
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