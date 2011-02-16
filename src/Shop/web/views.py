from django.http import HttpResponse
from django.template import Context, loader
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404
from models import Category, Product, Comment, User
import datetime

##
# Render  the index page. 
def index(request):
    template = loader.get_template('index.html')
    
    categories = Category.objects.all()
    best_products = Product.objects.filter(stock_count__gt=0).order_by('-average_rating')[:10]
    
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
    comments = Comment.objects.filter(product=product_id).order_by('timestamp')
    
    product.visit_count +=1;
    product.save()
    
    context = Context({
        'product':  product,
        'comments': comments,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))

##
# Publish a comment on a page 
def comment(request, product_id):
    template = loader.get_template('product.html')
      
    product = get_object_or_404(Product, id=product_id)
       
    text = request.POST['text']
    user_id = get_object_or_404(User, id=request.POST['user'])
    
    product.comment_count +=1;
    new_comment = Comment(product = product, 
                          user = user_id,
                          timestamp = datetime.datetime.now(),
                          comment = text)
    new_comment.save()
    product.save()
    
    comments = Comment.objects.filter(product=product_id).order_by('timestamp')
    
    context = Context({
        'product':  product,
        'comments': comments,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))

##
# Render a page with all the products of a specific category. 
def category(request, category_name):
    template = loader.get_template('list.html')
    thisCategorie = get_object_or_404(Category, name=category_name)
    categories = Category.objects.all()
    best_products = Product.objects.filter(category=thisCategorie.id).filter(stock_count__gt=0).order_by('-average_rating')[:10]
    
    context = Context({
        'this' : thisCategorie,
        'categories'  : categories,
        'products'    : best_products,
    })
    return HttpResponse(template.render(context))


##
# Render a simple registration form (sign up)
def signup(request):
    template = loader.get_template('signup.html')
    context = Context({
        'latest_poll_list': 'jarr',
    })
    return HttpResponse(template.render(context))

##
# Render a simple login form (sign in)
def signin(request):
    template = loader.get_template('signin.html')
    context = Context({
        'latest_poll_list': 'jarr',
    })
    return HttpResponse(template.render(context))
