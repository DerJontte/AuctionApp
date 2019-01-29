from django.shortcuts import redirect, render
from django.views import View
from auctionApp.forms import AddAuctionForm
from auctionApp.models import Auction


# TODO: Ready but needs comments
class EditAuction(View):
    def get(self, request, number):
        auction = Auction.objects.get(id=number)
        if request.user.id is not auction.seller_id:
            return redirect('home')
        request.session['to_update'] = number
        return render(request, 'auction_edit.html', {'form': AddAuctionForm(auction),
                                                     'auction_id': number})

    def post(self, request, number):
        if number == request.session['to_update']:
            auction = Auction.objects.get(id=number)
            auction.description = request.POST['description']
            auction.save()
            request.info_message = 'Auction successfully updated.'
        else:
            request.error_message = 'Error updating auction.'

        auction.time_posted = auction.time_posted.strftime('%d/%m/%y %H:%M')
        auction.time_closing = auction.time_closing.strftime('%d/%m/%y %H:%M')

        return render(request, 'auction_item_view.html', {'auction': auction})
