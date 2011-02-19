from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404
from models import Category, Product, Comment, User
from forms import CommentForm, SearchForm
import datetime

##
# Render  the index page. 
def index(request):
    template = loader.get_template('index.html')
    
    categories = Category.objects.all()
    best_products = Product.objects.filter(stock_count__gt=0).order_by('-average_rating')[:10]
    searchForm = SearchForm()
    
    context = Context({
        'categories'  : categories,
        'products'    : best_products,
        'form'        : searchForm,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))
    
    
##
# Render a specific product page.    
def product(request, product_id):
    template = loader.get_template('product.html')   
    product = get_object_or_404(Product, id=product_id)
    comments = Comment.objects.filter(product=product_id).order_by('timestamp')
    form = CommentForm()
    
    product.visit_count +=1;
    product.save()
    
    context = Context({
        'product':  product,
        'comments': comments,
        'form': form,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))


##
# Publish a comment on a page 
def comment(request, product_id):
    template = loader.get_template('product.html')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        
        if form.is_valid():
            product = get_object_or_404(Product, id=product_id)
            user_id = get_object_or_404(User, id=request.POST['user'])
            text = request.POST['comment']
    
            product.comment_count +=1;
            new_comment = Comment(product = product, 
                                  user = user_id,
                                  timestamp = datetime.datetime.now(),
                                  comment = text)
            
            new_comment.save()
            product.save()
    
            comments = Comment.objects.filter(product=product_id).order_by('timestamp')
    
    return HttpResponseRedirect('/product/%s' % (product_id))        


def rateComment(request, comment_id, option): 
    template = loader.get_template('product.html')
    comment = get_object_or_404(Comment, id=comment_id)
    
    if (option == '1'):
        comment.positives += 1
    else:
        comment.negatives -= 1
    
    comment.save()
    #return HttpResponse("%s <img src=\"/static/images/up.png\" onclick=\"rate(%s,1);\" />&nbsp;<img src=\"/static/images/down.png\" onclick=\"rate(%s,0);\" /> %s" % (comment.positives, comment.id, comment.id, comment.negatives))
    return HttpResponse("%s <img src=\"/static/images/up.png\" /> &nbsp;<img src=\"/static/images/down.png\"  /> %s" % (comment.positives, comment.negatives))


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
    context.update(csrf(request))
    return HttpResponse(template.render(context))

 
def search(request):
      
    if request.method == 'POST': # If the form has been submitted...
        form = SearchForm(request.POST) # A form bound to the POST data
        
        if form.is_valid(): # All validation rules pass
            query = form.cleaned_data['query']
            
            try: 
                products = Product.objects.filter(name__icontains = query)
            except Product.DoesNotExist: 
                return HttpResponse("Sorry, we can't find your product.")
           
            categories = Category.objects.all()            
            template = loader.get_template('list.html')
            message = "Search results for %s." % query
            context = Context({
                'message'     : message,
                'categories'  : categories,
                'products'    : products,
            })
            return HttpResponse(template.render(context))
           
    else:
        return HttpResponseRedirect('/')


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
