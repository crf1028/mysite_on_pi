from django.http import HttpResponse, Http404
from django.template.loader import get_template


def hello(request):
    return HttpResponse("Hello world")


def home(request):
    t = get_template('home_page.html')
    html = t.render()
    return HttpResponse(html)