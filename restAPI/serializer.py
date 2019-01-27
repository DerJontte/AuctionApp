from rest_framework import serializers
from auctionApp.models import Auction


class AuctionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Auction
        fields = ('id',
                  'seller_id',
                  'seller_name',
                  'seller_email',
                  'title',
                  'description',
                  'starting_price',
                  'current_price',
                  'current_winner_id',
                  'current_winner_name',
                  'time_posted',
                  'time_closing',
                  'active',
                  'banned',
                  'resolved')


