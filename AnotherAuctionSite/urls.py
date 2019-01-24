from django.contrib import admin
from django.urls import path, include

from auctionApp.account_management import EditUser, AddUser, ChangeCurrency
from auctionApp.add_auction import AddAuction
from auctionApp.bid_auction import BidAuction
from auctionApp.edit_auctions import EditAuction
from auctionApp.browse_auctions import Auctions
from auctionApp.login import Login, Logout
from auctionApp.search import Search
from auctionApp.views import BanAuction, ListBanned

urlpatterns = [
    path('', Auctions.as_view(), name='home'),

    path('auctions/<int:number>', Auctions.fetch_auction, name='auctionFetch'),
    path('auctions/add/', AddAuction.as_view(), name='auctionAdd'),
    path('auctions/edit/', Auctions.as_view(), name='auctionEdit'),
    path('auctions/edit/<int:number>', EditAuction.as_view(), name='auctionEdit'),
    path('auctions/bid/', BidAuction.as_view(), name='auctionBid'),
    path('auctions/bid/<int:number>', BidAuction.as_view(), name='auctionBid'),

    path('search/', Search.as_view(), name='search'),

    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('signup/', AddUser.as_view(), name='signup'),
    path('account-settings/', EditUser.as_view(), name='accountSettings'),
    path('change-currency/', ChangeCurrency.as_view(), name='changeCurrency'),

    path('admin/', admin.site.urls, name='admin'),
    path('admin_task/', BanAuction.as_view(), name='auctionBan'),
    path('admin_task/ban/<int:number>', BanAuction.as_view(), name='auctionBan'),
    path('admin_task/list_banned/', ListBanned.as_view(), name='auctionListBanned'),

    path('api/', include('restAPI.urls')),
]
