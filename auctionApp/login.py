from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views import View

from auctionApp.currency import Currency
from auctionApp.views import UserSettings


class Login(View):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                settings = UserSettings.objects.get(id=request.user.id)
                request.session['currency'] = settings.currency
                request.session['currencies'] = Currency.code_list()
        except:
            pass
        return redirect(request.META['HTTP_REFERER'])


class Logout(View):
    def post(self, request):
        logout(request)
        return redirect(request.META['HTTP_REFERER'])
