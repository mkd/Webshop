from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.template import Context, RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404

from models import Category, Product, Comment, User, UserProfile
from forms import CommentForm
import datetime, hashlib

##
# Render the home page. 
def index(request):
    
    template = loader.get_template('index.html')
    categories = Category.objects.all()
    best_products = Product.objects.filter(stock_count__gt=0).order_by('-average_rating')[:10]
    searchForm = SearchForm()
    
    # check for an existing session
    if request.session.get('id', False):
        context = Context({
            'signed_in'   : True,
            'user'        : User.objects.get(id=request.session.get('id')).username,
            'categories'  : categories,
            'products'    : best_products,
            'form'        : searchForm,
        })
    # if no session, use a standard context
    else:
        context = Context({
            'signed_in'   : False,
            'user'        : None,
            'categories'  : categories,
            'products'    : best_products,
            'form'        : searchForm,
        })

    # render the home page
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
    context = RequestContext(request, { })
    return HttpResponse(template.render(context))


##
# Render a simple login form (sign in)
def signin(request):
    t = loader.get_template('signin.html')
    context = RequestContext(request, { })
    return HttpResponse(t.render(context))


##
# Perform the actual login.
#
# This function checks the user and password against the users in the database
# and tries to log in. If successful, the user is redirected to the home page,
# otherwise an error is displayed.
def login(request):
    u = User.objects.get(username=request.POST['user'])
    p = u.password
    # user and password match
    if u.password == hashlib.sha1(request.POST['pass']).hexdigest():
        request.session['id'] = u.id
        t = loader.get_template('index.html')
        context = Context({
            'user': request.POST['user'],
            'pass': request.POST['pass'],
            'stored_pass': u.password,
            'signed_in' : True,
            'login_failed' : False,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))
    # login failed
    else:
        t = loader.get_template('signin.html')
        context = Context({
            'user': None,
            'signed_in' : False,
            'login_failed': True,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Close the session for an user.
def signout(request):
    t = loader.get_template('index.html')
    context = RequestContext(request, { 
        'user': None,
        'signed_in': False,
    })
    try:
        del request.session['id']
    except KeyError:
        pass
    return HttpResponse(t.render(context))


##
# Add a new user.
def register(request):
    t = loader.get_template('index.html')
    if request.method == 'POST':
        context = Context({
            'user': request.POST['user'],
            'pass': request.POST['pass'],
            'signed_in' : True,
            'login_failed' : False,
        })
        
        # save all the data from the POST into the database
        u = User(
            username       = request.POST['user'],
            first_name     = request.POST['fname'],
            last_name      = request.POST['sname'],
            email          = request.POST['email'],
            password       = hashlib.sha1(request.POST['pass']).hexdigest(),
        )
        u.save()

        # redirect the user to the home page (already logged-in)
        return HttpResponseRedirect(t.render(context))


##
# Render the user profile page.
def profile(request):
    # check for an existing session
    if request.session.get('id', False):
        t = loader.get_template('profile.html')

        # obtain the data from the user and display his/her profile
        u = UserProfile.objects.get(id=request.session.get('id'))
        context = Context({
            'picture'        : u.picture,
            'first_name'     : u.first_name,
            'last_name'      : u.last_name,
            'email'          : u.email,
            'postal_address' : u.postal_address,
            'postal_code'    : u.postal_code,
            'postal_city'    : u.postal_city,
            'postal_country' : u.postal_country,
        })
        return HttpResponseRedirect(t.render(context))
    # if no session, use a standard context
    else:
        render_for_response('index.html', locals())
