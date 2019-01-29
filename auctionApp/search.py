from django.shortcuts import redirect
from django.views import View


# TODO: ready.
class Search(View):
    def post(self, request):
        if 'search' in request.POST:
            query = str(request.POST['search']).lower()
            request.session['search_query'] = query
        return redirect('home')
