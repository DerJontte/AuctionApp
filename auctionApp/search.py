from django.shortcuts import redirect
from django.views import View

global results
results = ''


class Search(View):
    global results

    def post(self, request):
        if 'search' in request.POST:
            query = str(request.POST['search']).lower()
            request.session['search_query'] = query
        return redirect('home')
