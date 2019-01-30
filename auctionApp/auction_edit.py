from django.shortcuts import redirect, render
from django.views import View
from auctionApp.forms import AddAuctionForm
from auctionApp.models import Auction


class EditAuction(View):
    def get(self, request, number):
        # Check that the user is the owner of the auction and render the editing page
        auction = Auction.objects.get(id=number)
        if request.user.id is not auction.seller_id:
            return redirect('home')
        return render(request, 'auction_edit.html', {'form': AddAuctionForm(auction),
                                                     'auction_id': number})

    def post(self, request, number):
        auction = Auction.objects.get(id=number)

        # If the user is the owner of the auction, update description and save
        if request.user.id is auction.seller_id:
            auction.description = request.POST['description']
            auction.save()

            # Format the timestamps for displaying
            auction.time_posted = auction.time_posted.strftime('%d/%m/%y %H:%M')
            auction.time_closing = auction.time_closing.strftime('%d/%m/%y %H:%M')
            request.info_message = 'Auction successfully updated.'
        else:
            request.error_message = 'Authorization error.'

        return render(request, 'auction_item_view.html', {'auction': auction})
