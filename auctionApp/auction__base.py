from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime

from auctionApp.currency import Currency
from auctionApp.models import Auction
from auctionApp.views import admin_mail


class Auctions(View):
    def get(self, request, **kwargs):
        Currency.assert_currency(request)

        if 'number' in kwargs:
            return None

        if 'banned' in request.GET and request.user.is_superuser:
            auctions = Auction.objects.all().filter(banned=True)
            request.error_message = 'This is a list of banned auctions.'
        else:
            auctions = Auction.objects.all().filter(active=True, time_closing__gte=datetime.now())
        auctions = auctions.order_by('time_closing')

        if 'search_query' in request.session:
            auctions = auctions.filter(title__contains=request.session['search_query'])
            del request.session['search_query']

        for auction in auctions:
            auction.time_closing = auction.time_closing.strftime('%d/%m/%y %H:%M')
            if request.session['currency'] != 'EUR':
                converted_price = Currency.exchange(auction.current_price, request.session['currency'])
                auction.current_price = "%.2f" % converted_price

        return render(request, 'auction_listing.html', {'auctions': auctions})

    def fetch_auction(request, number):
        Currency.assert_currency(request)
        try:
            auction = Auction.objects.get(id=number)
        except ObjectDoesNotExist:
            return redirect('home')

        if auction.banned and not request.user.is_superuser:
            request.error_message = 'The auction you are trying to view has been banned'
            return redirect('home')

        auction.time_posted = auction.time_posted.strftime('%d/%m/%y %H:%M')
        auction.time_closing = auction.time_closing.strftime('%d/%m/%y %H:%M')

        auction.starting_converted = Currency.exchange(auction.starting_price, request.session['currency'])
        auction.current_converted = Currency.exchange(auction.current_price, request.session['currency'])

        return render(request, 'auction_item_view.html', {'auction': auction})


class BanAuction(View):
    def post(self, request, number):
        if request.POST['action'] == 'Ban':
            auction = Auction.objects.get(id=number)
            auction.banned = True
            auction.active = False
            auction.save()

            subject = 'Auction has been banned'
            message = 'The auction %d: "%s" has been banned because it violates the YAAS TOS. No further bidding on the item is possible and ' \
                      'the auction will not be resolved.' % (auction.id, auction.title)
            recipients = [auction.seller_email]
            for bidder in auction.bid_set.all():
                if bidder.email not in recipients:
                    recipients.append(bidder.email)
            send_mail(subject, message, admin_mail, recipients, fail_silently=False)
            request.error_message='Auction banned.'
            return Auctions.fetch_auction(request, number)

        if request.POST['action'] == 'Unban':
            auction = Auction.objects.get(id=number)
            auction.banned = False
            auction.active = True
            auction.save()

            subject = 'Auction unbanned'
            message = 'Your auction %d: "%s" has been unbanned and can be bid on again.' % (auction.id, auction.title)
            recipient = auction.seller_email
            send_mail(subject, message, admin_mail, [recipient], fail_silently=False)
            request.info_message = 'Auction unbanned.'
            return Auctions.fetch_auction(request, number)


