from django.urls import path
from restAPI import views

urlpatterns = [
    path('auctions/', views.auction_list),
    path('auctions/<int:number>', views.auction_detail),
    path('auctions/query=<slug:query>', views.auction_search),
]
