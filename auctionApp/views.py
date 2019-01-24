import re
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views import View

from auctionApp.browse_auctions import Auctions
from auctionApp.models import *

admin_mail = 'broker@awesomeauctions.com'


class ListBanned(View):
    def get(self, request):
        if not request.user.is_superuser:
            return redirect('home')
        auctions = Auction.objects.all().filter(banned=True)
        request.error_message = 'This is a list of banned auctions.'
        return render(request, 'home.html', {'auctions': auctions})


class BanAuction(View):
    def get(self, request):
        return redirect('home')

    def post(self, request, number):
        if request.POST['action'] == 'Ban':
            auction = Auction.objects.get(id=number)
            auction.banned = True
            auction.active = False
            auction.save()

            subject = 'Auction has been banned'
            message = 'The auction %d: "%s" has been banned because it violates the YAAS TOS. No further bidding on the item is possible and ' \
                      'the auction will not be resolved.' % (auction.id, auction.title)
            recipients = []
            recipients.append(auction.seller_email)
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


def handler404(request, *args, **argv):
    return redirect('/home/')


def make_slug_hash(input):
    input = make_password(input)
    output = re.sub('(\W)|(pbkdf2_sha256)', '', input);
    return output


