from django.http import HttpResponse, Http404


def hello(request):
    return HttpResponse("Hello world")