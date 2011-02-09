from django.http import HttpResponse
from django.template import Context, loader
from models import Category, Product

def index(request):
    template = loader.get_template('index.html')
    
    categories = Category.objects.all()
    best_products = Product.objects.all().order_by('average_rating')[:5].reverse()
    
    context = Context({
        'categories'  : categories,
        'products'    : best_products,
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

def signup(request):
    template = loader.get_template('signup.html')
    context = Context({
        'latest_poll_list': 'jarr',
    })
    return HttpResponse(template.render(context))
