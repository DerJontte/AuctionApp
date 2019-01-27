from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views import View
from auctionApp.currency import Currency
from auctionApp.forms import AddAuctionForm
from auctionApp.models import Auction
from auctionApp.auction__base import Auctions, admin_mail


# This one is ready, just the comments missing
class AddAuction(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('home')

        Currency.assert_currency(request)

        min_date = (datetime.now() + timedelta(hours=72)).strftime('%Y-%m-%dT%H:%M')
        max_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%dT%H:%M')

        return render(request, 'auction_add.html', {'form': AddAuctionForm,
                                                    'rate': Currency.get_rate(request.session['currency']),
                                                    'min_date': min_date,
                                                    'max_date': max_date})

    def post(self, request):
        form = AddAuctionForm(request.POST)
        if form.is_valid():
            request.session['unsaved_auction'] = True
            data = form.cleaned_data

            parts = request.POST['end_datetime'].split('T')
            date = list(map(int, parts[0].split('-')))
            time = list(map(int, parts[1].split(':')))
            time_closing = datetime(year=date[0], month=date[1], day=date[2], hour=time[0], minute=time[1])

            time_posted = datetime.now()

            request.session['time_closing'] = str(time_closing)
            request.session['time_posted'] = str(time_posted)

            global auction
            auction = Auction(seller_id=request.user.id,
                              seller_name=request.user.username,
                              seller_email=request.user.email,
                              title=data['title'],
                              description=data['description'],
                              starting_price=data['starting_price'],
                              current_price=data['starting_price'],
                              time_closing=time_closing.strftime('%d/%m/%y %H:%M'),
                              time_posted=time_posted.strftime('%d/%m/%y %H:%M'))

            auction.starting_converted = Currency.exchange(auction.starting_price, request.session['currency'])
            auction.current_converted = Currency.exchange(auction.current_price, request.session['currency'])

            return render(request, 'auction_confirm.html', {'auction': auction})

        if 'confirmed' not in request.POST:
            if 'unsaved_auction' in request.session:
                del request.session['unsaved_auction']
                del auction
            return redirect('home')

        if 'unsaved_auction' not in request.session:
            request.error_message = 'No pending auction or auction has already been added.'
            return Auctions.get(None, request)

        auction.time_posted = request.session['time_posted']
        auction.time_closing = request.session['time_closing']
        auction.save()

        message_body = 'Your auction has been created with the title "' + auction.title + '".'
        send_mail('Auction created',
                  message_body,
                  admin_mail,
                  [request.user.email])

        del request.session['unsaved_auction']
        request.info_message = 'Auction added'
        return Auctions.fetch_auction(request, auction.id)
