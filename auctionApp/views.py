from django.shortcuts import render

admin_mail = 'broker@awesomeauctions.com'


def handler404(request, *args, **argv):
    return render(request, '404.html')
