from django.db import transaction
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
        return render(request, 'auction_edit.html', {'form': form,
                                                     'auction_id': number})

    def post(self, request, number):
        with transaction.atomic():
            if number == request.session['to_update']:
                auction = Auction.objects.select_for_update().get(id=number)
                auction.description = request.POST['description']
                auction.save()
                request.info_message = 'Auction successfully updated.'
            else:
                request.error_message = 'Error updating auction.'

        auction.time_posted = auction.time_posted.strftime('%d/%m/%y %H:%M')
        auction.time_closing = auction.time_closing.strftime('%d/%m/%y %H:%M')
        return render(request, 'auction_item_view.html', {'auction': auction})
