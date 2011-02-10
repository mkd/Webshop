from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from models import Category, Product

##
# Render  the index page. 
def index(request):
    template = loader.get_template('index.html')
    
    categories = Category.objects.all()
    best_products = Product.objects.all().order_by('average_rating').reverse()[:10]
    
    context = Context({
        'categories'  : categories,
        'products'    : best_products,
    })
    return HttpResponse(template.render(context))
    
##
# Render a specific product page.    
def product(request, product_id):
    template = loader.get_template('product.html')   
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    
    context = Context({
        'categories'  : categories,
        'product': product,
    })
    return HttpResponse(template.render(context))

##
# Render a page with all the products of a specific category. 
def category(request, category_name):
    template = loader.get_template('list.html')
    thisCategorie = get_object_or_404(Category, name=category_name)
    categories = Category.objects.all()
    best_products = Product.objects.filter(category=thisCategorie.id).order_by('average_rating').reverse()[:10]
    
    context = Context({
        'this' : thisCategorie,
        'categories'  : categories,
        'products'    : best_products,
    })
    return HttpResponse(template.render(context))


def signup(request):
    template = loader.get_template('signup.html')
    context = Context({
        'latest_poll_list': 'jarr',
    })
    return HttpResponse(template.render(context))
