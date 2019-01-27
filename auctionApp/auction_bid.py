from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views import View

from auctionApp.auction__base import Auctions
from auctionApp.currency import Currency
from auctionApp.models import Auction
from auctionApp.views import admin_mail


class BidAuction(View):
    def post(self, request, number):
        # TODO: kolla om Currency.assert funkar, och om det överhuvudtaget behövs (finns det nån caller som int gör detta?)
        if 'currency' in request.session:
            currency = request.session['currency']
        else:
            currency = 'EUR'

        if 'place-bid' in request.POST:
            return self.place_bid(request, number, currency)

        if 'confirm' in request.POST:
            return self.confirm_bid(request, number)

        return redirect(request.META['HTTP_REFERER'])

    def place_bid(self, request, number, currency):
        if request.user.is_authenticated:
            new_bid = float(request.POST['starting_price'])
            auction = Auction.objects.get(id=number)
            if request.user.id == auction.current_winner_id:
                # This is a request that should not be accessible through the app, so a simple 403 will suffice
                return HttpResponseForbidden()
            if currency != 'EUR':
                converted_bid = Currency.exchange(new_bid, currency)
                converted = '(%.2f %s)' % (converted_bid, currency)
            else:
                converted = ''
            question = 'Do you want to bid %s EUR %s on this auction?' % (new_bid, converted)
            request.session['description'] = auction.description
            return render(request, 'bid_confirm.html', {'auction': auction,
                                                        'bid': float(new_bid),
                                                        'question': question})
        else:
            return HttpResponseForbidden('User not logged in')

    def confirm_bid(self, request, number):
        auction = Auction.objects.get(id=number)

        if request.user.id == auction.current_winner_id:
            # This is a request that should not be accessible through the app, so return 403
            return HttpResponseForbidden('You can not bid on an auction you\'re already winning.')

        # Check that the current description is the same as the one the bidder has seen and continue
        if auction.description != request.session['description']:
            request.error_message = 'Bid was not registered: Auction description has been changed. Please see new description before bidding again.'
            return Auctions.fetch_auction(request, number)

        new_winner = request.user.username
        seller_email = auction.seller_email
        new_bid = float(request.POST['bid'])

        try:
            old_winner_email = User.objects.get(id=auction.current_winner_id).email
        except:
            old_winner_email = None

        tf = '%Y%m%d%H%M%S'
        current_time = datetime.now().strftime(tf)
        closing_time = auction.time_closing.strftime(tf)

        # Make sure the new bid is higher than the current bid and that the auction is still open,
        # then continue
        if new_bid > auction.current_price and current_time <= closing_time:
            auction.current_price = new_bid
            auction.current_winner_id = request.user.id
            auction.current_winner_name = request.user.username
            auction.bid_set.create(user_id=request.user.id, name=request.user.username, email=request.user.email, price=new_bid)

            # When subtracting closing_time and current_time as integers with the format defined above, the
            # last four relevant numbers will be minutes and seconds. Thus, a diff smaller than 500 will
            # mean that there is less than 5 minutes left of the auction. If that's the case, the auction
            # will be extended to end 5 minutes after the last bid.
            diff = int(closing_time) - int(current_time)
            if diff < 500:
                auction.time_closing = datetime.now() + timedelta(seconds=300)
            auction.save()
            request.info_message = 'Your bid has been registered'
        else:
            if new_bid <= auction.current_price:
                request.error_message = 'Bid could not be registered: an older bid is higher.'
            if current_time > closing_time:
                request.error_message = 'Bid could not be registered: auction deadline has passed.'
            return Auctions.fetch_auction(request, number)

        to_seller = 'A new bid has been registered for your auction "' + str(auction.title) + '".'
        send_mail('A new bid has been registered',
                  to_seller,
                  admin_mail,
                  [seller_email])

        if old_winner_email is not None:
            to_old_winner = 'Your winning bid in the auction "' + str(auction.title) + '" has been outbidded.'
            send_mail('Your bid has been beaten',
                      to_old_winner,
                      admin_mail,
                      [old_winner_email])

        return Auctions.fetch_auction(request, number)
