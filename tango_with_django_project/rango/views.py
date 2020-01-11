from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # Refer to the TwD book for more information on how this updated view works.
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return HttpResponse("Rango says here is the about page. <a href='/rango/'>Index</a>")