from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View
from auctionApp.auction__base import Auctions
from auctionApp.forms import AddNewUserForm, EditUserForm
from auctionApp.models import UserSettings


# TODO: Comments
class AddUser(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, "signup.html", {'signup_form': AddNewUserForm})

    def post(self, request):
        form = AddNewUserForm(request.POST)

        if not form.is_valid():
            request.error_message = form.errors['__all__'][0]
            return render(request, 'signup.html', {'signup_form': form})

        data = form.cleaned_data
        username = data['username']

        new_user = User(username=username, email=data['email'], password=make_password(data['password']))
        new_user.save()

        user_settings = UserSettings(id=request.user.id, currency=data['currency'])
        user_settings.save()

        request.info_message = 'New account created for user ' + str(new_user.username)
        return Auctions.get(self, request)


class EditUser(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('home')

        form = EditUserForm()
        form.initial['email'] = request.user.email
        return render(request, "account_settings.html", {'form': form})

    def post(self, request):
        form = EditUserForm(request.POST)
        if not form.is_valid():
            request.error_message = form.errors['__all__'][0]
            return render(request, 'account_settings.html', {'form': form})

        data = form.cleaned_data
        user = request.user
        email = data['email']
        password = data['new_password']

        if not user.check_password(data['old_password']):
            request.error_message = 'Password error'
            return render(request, 'account_settings.html', {'form': form})

        request.info_message = ''

        if email != request.user.email:
            user.email = email
            user.save()
            request.info_message += 'Email changed to ' + email + '\n'

        if user.check_password(password):
            request.error_message = 'New password cannot be the same as old password.'
        elif password is not '':
            user.set_password(password)
            user.save()
            logout(request)
            request.info_message += 'Password changed. Please login with your new password.\n'
            return Auctions.get(None, request)
        return self.get(request)


class ChangeCurrency(View):
    def post(self, request):
        currency = request.POST['currency']
        request.session['currency'] = currency

        if request.user.is_authenticated:
            if request.user.id in UserSettings.objects.all():
                usersettings = UserSettings.objects.get(id=request.user.id)
                usersettings.currency = currency
            else:
                usersettings = UserSettings(id=request.user.id, currency=currency)
            usersettings.save()
        return redirect(request.META['HTTP_REFERER'])