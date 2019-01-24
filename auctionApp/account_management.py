from sqlite3 import IntegrityError

from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View

from auctionApp.browse_auctions import Auctions
from auctionApp.currency import Currency
from auctionApp.forms import AddNewUserForm, EditUserForm
from auctionApp.views import UserSettings


class AddUser(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        signup_form = AddNewUserForm
        return render(request, "signup.html", {'signup_form': signup_form})

    def post(self, request):
        form = AddNewUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            if not data['password1'] == data['password2']:
                request.error_message = 'Passwords do not match'
                return render(request, 'signup.html', {'signup_form': form})
            else:
                password = make_password(data['password1'])
            email = data['email']
            try:
                User.objects.get(username=username)
                request.error_message = "User name is already taken, please choose another name."
                return render(request, 'signup.html', {'signup_form': form})
            except:
                new_user = User(username=username, email=email, password=password)
                user_settings = UserSettings(id=request.user.id, currency=data['currency'])
                user_settings.save()
                new_user.save()
                request.info_message = 'New account created for user ' + str(new_user.username)
                return Auctions.get(self, request)
        else:
            request.error_message = 'Sorry, something went wrong. Please check all fields and try again.'
            return render(request, 'signup.html', {'signup_form': form})


class EditUser(View):
    global options
    options = Currency.code_list()

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('home')
        form = EditUserForm(initial={'email': request.user.email})
        return render(request, "user_settings.html", {'page_name': 'Edit account information',
                                                      'form': form,
                                                      'options': options})

    def post(self, request):
        form = EditUserForm(request.POST)
        if form.is_valid():
            info_message = ''
            error_message = ''
            user = request.user
            data = form.cleaned_data
            email = data['email']
            password1 = data['new_password1']
            password2 = data['new_password2']
            if user.check_password(data['old_password']):
                if email != request.user.email:
                    user.email = email
                    user.save()
                    info_message = info_message.__add__('Email changed to ' + email + "\n")
                if password1 and password2:
                    if password1 == password2:
                        if not user.check_password(password1):
                            user.set_password(password1)
                            user.save()
                            logout(request)
                            info_message = info_message.__add__(
                                'Password changed. Please login with your new password.\n')
                            return render(request, 'home.html', {'info_message': info_message})
                        else:
                            error_message = 'New password cannot be the same as old password.'
                    else:
                        error_message = 'Passwords do not match'
            return render(request, 'user_settings.html', {'form': form,
                                                         'error_message': error_message,
                                                         'info_message': info_message,
                                                         'options': options, })


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