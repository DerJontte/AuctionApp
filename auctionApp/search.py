from django.shortcuts import redirect
from django.views import View


class Search(View):
    def post(self, request):
        if 'search' in request.POST:
            query = str(request.POST['search']).lower()
            request.session['search_query'] = query  # Save the query in a session variable, otherwise it won't survive the redirect
        return redirect('home')
