from django.contrib.auth.models import User
from django import forms
from auctionApp.currency import Currency


class LoginForm(forms.Form):
    username = forms.CharField(initial='Username', max_length=20)
    password = forms.CharField(initial='Password', widget=forms.PasswordInput())


class AddNewUserForm(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    password_repeat = forms.CharField(widget=forms.PasswordInput(), label='Re-type password')
    currency = forms.CharField(widget=forms.Select(choices=Currency.code_list(list_type='pairlist')), label='What is your currency?', initial='EUR')

    def clean(self):
        # When validating the form, check that the username is free and that the repeated passwords match. If not,
        # reply with an error message
        cleaned_data = super().clean()
        if User.objects.filter(username=cleaned_data['username']).exists():
            self.add_error(None, 'Username is already taken')
        elif cleaned_data['password'] != cleaned_data['password_repeat']:
            self.add_error(None, 'Passwords do not match')
        return cleaned_data


class EditUserForm(forms.Form):
    email = forms.EmailField(label='E-mail', required=False)
    new_password = forms.CharField(label = 'New password', widget=forms.PasswordInput(), required=False)
    new_password_repeat = forms.CharField(label ='Re-enter new password', widget=forms.PasswordInput(), required=False)
    old_password = forms.CharField(label = 'Current password (required)', widget=forms.PasswordInput(), required=True)

    def clean(self):
        # Check that the repeated passwords match if applicable
        cleaned_data = super().clean()
        if cleaned_data['new_password'] != cleaned_data['new_password_repeat']:
            self.add_error(None, "Passwords do not match")
        return cleaned_data


class AddAuctionForm(forms.Form):
    title = forms.CharField(label="Auction title", max_length=100)
    description = forms.Field(widget=forms.Textarea)
    starting_price = forms.FloatField(initial=0)


class CurrencyPicker(forms.Form):
    currency = forms.CharField(widget=forms.Select(choices=Currency.code_list(list_type='pairlist')), label='Currency')
