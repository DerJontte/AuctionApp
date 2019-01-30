from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from restAPI.serializer import AuctionSerializer
from auctionApp.models import Auction


@csrf_exempt
def auction_list(request):
    # List all auctions that are active, not banned and not resolved.
    if request.method == 'GET':
        auctions = Auction.objects.all().filter(active=True, banned=False, resolved=False).order_by('time_closing')
        serializer = AuctionSerializer(auctions, many=True)
        return JsonResponse(serializer.data, safe=False)


# Get a list of all active, not banned, not resolved auctions that contain the queried string
@csrf_exempt
def auction_search(request, query):
    if request.method == 'GET':
        auctions = Auction.objects.all().filter(active=True, resolved=False, banned=False, title__contains=query)
        serializer = AuctionSerializer(auctions, many=True)
        return JsonResponse(serializer.data, safe=False)


# Retrieve information about a specific auction
@csrf_exempt
def auction_detail(request, number):
    try:
        auction = Auction.objects.get(pk=number)
    except Auction.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AuctionSerializer(auction)
        return JsonResponse(serializer.data)


# Post a new auction
@csrf_exempt
def auction_add(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = AuctionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
