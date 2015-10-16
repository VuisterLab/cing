from django.http import HttpResponse
from django.template import RequestContext, loader


def index(request):
    template = loader.get_template('iCing/index.html')
    context = {}
    return HttpResponse(template.render(context))
