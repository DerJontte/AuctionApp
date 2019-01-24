import time
from re import split

from django.db import transaction
from django.db.backends import sqlite3
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from auctionApp.forms import AddAuctionForm
from auctionApp.models import Auction


class EditAuction(View):
    def get(self, request, number):
        auction = Auction.objects.get(id=number)
        owner = request.user.id == auction.seller_id
        if not owner:
            return redirect('home')
        request.session['to_update'] = number
        form = AddAuctionForm(auction)
        return render(request, 'auction_item_edit.html', {'form': form,
                                                          'auction_id': number})

    def post(self, request, query):
        with transaction.atomic():
            if request.POST['id'] == request.session['to_update']:
                auction = Auction.objects.select_for_update().get(hash_id=request.POST['id'])
                auction.description = request.POST['description']
                auction.save()
                error_message = None
                info_message = 'Auction successfully updated.'
            else:
                error_message = 'Error updating auction.'
                info_message = None

        return render(request, 'view_auction.html', {'auction': auction,
                                                     'error_message': error_message,
                                                     'info_message': info_message})
