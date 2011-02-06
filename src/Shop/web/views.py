from django.http import HttpResponse
from django.template import Context, loader

def index(request):
    template = loader.get_template('index.html')
    context = Context({
        'latest_poll_list': 'jarr',
    })
    return HttpResponse(template.render(context))
    
def product(request):
    template = loader.get_template('product.html')
    context = Context({
        'latest_poll_list': 'jarr',
    })
    return HttpResponse(template.render(context))

def category(request):
    template = loader.get_template('index.html')
    context = Context({
        'latest_poll_list': 'jarr',
    })
    return HttpResponse(template.render(context))