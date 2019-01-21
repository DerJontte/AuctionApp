import time
from re import split

from django.db import transaction
from django.db.backends import sqlite3
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from auctionApp.forms import AddAuctionForm
from auctionApp.models import Auction


class EditAuction(View):
    def get(self, request, query):
        auction = Auction.objects.get(hash_id=query)
        owner = request.user.id == auction.seller_id
        if request.user.is_authenticated and not owner:
            error_message = 'You do not have permission to edit this auction.'
            return render(request, 'view_auction.html', {'auction': auction,
                                                              'owner': owner,
                                                              'error_message': error_message})
        request.session['to_update'] = query
        form = AddAuctionForm(auction)
        return render(request, 'edit_auction_item.html', {'form': form,
                                                          'auction_id': query})

    def post(self, request, query):
        with transaction.atomic():
            error_message = 'Error updating auction.'
            info_message = None
            if request.POST['id'] == request.session['to_update']:
                auction = Auction.objects.select_for_update().get(hash_id=request.POST['id'])
                auction.description = request.POST['description']
                auction.save()
                error_message = None
                info_message = 'Auction successfully updated.'
        owner = request.user.id == auction.seller_id

        stripped = split('edit', request.META['HTTP_REFERER'])[0]
        request.session['override'] = stripped + str(auction.id)

        return render(request, 'view_auction.html', {'auction': auction,
                                                          'owner': owner,
                                                          'error_message': error_message,
                                                          'info_message': info_message})
