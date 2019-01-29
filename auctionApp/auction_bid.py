from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime, timedelta
from auctionApp.auction__base import Auctions
from auctionApp.currency import Currency
from auctionApp.models import Auction
from auctionApp.views import admin_mail


# TODO: Allt klart
class BidAuction(View):
    def post(self, request, number):
        # User must be logged in to be able to bid on an auction
        if not request.user.is_authenticated:
            return HttpResponseForbidden('User not logged in')

        # If the user has placed the bid on the item page, ask them to confirm the bid
        if 'place-bid' in request.POST:
            return self.confirm_bid(request, number)

        # When the user has confirmed the bid, save it to the database
        if 'confirm' in request.POST:
            return self.save_bid(request, number)

        # If the user chose not to save the bid, return to the listing
        request.error_message = 'Bid not saved'
        return Auctions.get(None, request)

    def confirm_bid(self, request, number):
        auction = Auction.objects.get(id=number)

        if request.user.id == auction.current_winner_id:
            # This is a request that should not be accessible through the app, so a simple 403 will suffice
            return HttpResponseForbidden()

        # Format the bid confirmation according to the user's currency
        currency = request.session['currency']
        new_bid = request.POST['starting_price']
        converted_bid = new_bid if currency is 'EUR' else Currency.exchange(float(new_bid), currency)
        display_bid = 'Do you want to bid %.2f %s on this auction?' % (converted_bid, currency)

        # Use (or "abuse") the error_message to display this rather important question to the user
        request.error_message = display_bid
        request.bid = new_bid
        request.session['description'] = auction.description  # Save the description for later assessment
        return render(request, 'bid_confirm.html', {'auction': auction})

    def save_bid(self, request, number):
        auction = Auction.objects.get(id=number)

        if request.user.id == auction.current_winner_id:
            # This is a request that should not be accessible through the app, so return 403
            return HttpResponseForbidden('You can not bid on an auction you\'re already winning.')

        # Check that the current description is the same as the one the bidder has seen and continue
        if auction.description is not request.session['description']:
            request.error_message = 'Bid was not registered: Auction description has been changed. Please see new description before bidding again.'
            return Auctions.fetch_auction(request, number)

        # Store the previus winner's e-mail so we can notify him/her
        try:
            old_winner_email = User.objects.get(id=auction.current_winner_id).email
        except:
            old_winner_email = None

        # Make sure the new bid is still open
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        closing_time = auction.time_closing.strftime('%Y%m%d%H%M%S')
        if current_time > closing_time:
            request.error_message = 'Bid could not be registered: auction deadline has passed.'
            return Auctions.fetch_auction(request, number)

        # Make sure the new bid is still higher than the newest bid
        new_bid = float(request.POST['bid'])
        if new_bid <= auction.current_price:
            request.error_message = 'Bid could not be registered: someone has made a higher bid.'
            return Auctions.fetch_auction(request, number)

        # Update the auction with data about the new highest bid
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

        # Save the updated auction
        auction.save()

        # Notify the user, the auction owner and the outbidded user about the new winning bid
        request.info_message = 'Your bid has been registered'

        seller_email = auction.seller_email
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
