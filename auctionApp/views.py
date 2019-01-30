from django.shortcuts import render


def handler404(request, *args, **argv):
    request.error_message = "Sorry, we could not find what you are looking for."
    return render(request, '404.html')
