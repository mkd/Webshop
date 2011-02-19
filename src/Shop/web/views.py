from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.template import Context, RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from models import Category, Product, Comment, User, UserProfile, CartProduct
from forms import CommentForm, SearchForm, RegisterForm, ProfileForm
import datetime, hashlib, os

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
        'product'  : product,
        'comments' : comments,
        'form'     : form,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))


##
# Render the user cart page.    
def cart(request, user_id):
    print user_id
    template = loader.get_template('cart.html')
    user = get_object_or_404(User, id=user_id)
    userProducts = CartProduct.objects.filter(user=user)
        
    context = Context({
        'cart'  : userProducts,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))

def deleteFromCart(request):
    if request.method == 'POST':
        element = request.POST['product']

##
# Publish a comment on a page 
def comment(request, product_id):
    template = loader.get_template('product.html')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        
        if form.is_valid():
            product = get_object_or_404(Product, id=product_id)
            user_id = get_object_or_404(User, id=request.POST['user'])
            text = form.cleaned_data['comment']
            reply = Comment.objects.get(id=request.POST['in_reply'])
    
            product.comment_count +=1;
            
            if reply:
                new_comment = Comment(product = product, 
                                      user = user_id,
                                      timestamp = datetime.datetime.now(),
                                      comment = text,
                                      parent_id = reply)
            else:
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
    return HttpResponse("<a onclick=\"showReplyBox('%s');\">Reply</a> | %s <img src=\"/static/images/up.png\" /> &nbsp;<img src=\"/static/images/down.png\"  /> %s" % (comment.id, comment.positives, comment.negatives))


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
                return HttpResponse("Sorry, we couldn't find your product.")
           
            categories = Category.objects.all()            
            template = loader.get_template('list.html')
            message = "Search results for %s." % query
            context = Context({
                'message'     : message,
                'categories'  : categories,
                'products'    : products,
            })
            
            context.update(csrf(request))
            return HttpResponse(template.render(context))
           
    else:
        return HttpResponseRedirect('/')


##
# Render a simple registration form (sign up)
def signup(request):
    template = loader.get_template('signup.html')
    form = RegisterForm()
    context = RequestContext(request,
    {
        'form': form,
    })
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
    try:
        u = User.objects.get(username=request.POST['user'])
    except User.DoesNotExist:
        t = loader.get_template('signin.html')
        context = Context({
            'login_failed' : True,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))
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
        form = RegisterForm(request.POST, request.FILES)
        # check if the user already exists in the database
        try:
            check_username = User.objects.get(username=request.POST['user'])
        except:
            check_username = None
        try:
            check_email = User.objects.get(email=request.POST['email'])
        except:
            check_email = None
        if check_username is not None or check_email is not None:
            t = loader.get_template('signup.html')
            context = Context({
                'username'       : request.POST['user'],
                'fname'          : request.POST['fname'],
                'sname'          : request.POST['sname'],
                'email'          : request.POST['email'],
                'email2'         : request.POST['email2'],
                'passwd'         : request.POST['passwd'],
                'pass2'          : request.POST['pass2'],
                'user_exists'    : True,
                'form'           : form
            })
            context.update(csrf(request))
            return HttpResponse(t.render(context))

        # save also avatar picture, if available
        if form.is_valid():
            handle_uploaded_profile_pic(request.FILES['picture'], request.POST['user'] + '.jpg')
        
        # save all the data from the POST into the database
        context = Context({
            'signed_in' : True,
            'user'      : request.POST['user'],
        })
        u = User(
            username       = request.POST['user'],
            first_name     = request.POST['fname'],
            last_name      = request.POST['sname'],
            email          = request.POST['email'],
            password       = hashlib.sha1(request.POST['passwd']).hexdigest(),
        )
        u.save()

        # redirect the user to the home page (already logged-in)
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Render the user profile page.
def profile(request):
    # check for an existing session
    if request.session.get('id', False):
        t = loader.get_template('profile.html')
        form = ProfileForm(request.POST, request.FILES)

        # obtain the data from the user and display his/her profile
        u = User.objects.get(id=request.session.get('id'))
        context = Context({
            'picture'        : '/static/images/users/' + u.username + '.jpg',
            'user'           : u.username,
            'fname'          : u.first_name,
            'sname'          : u.last_name,
            'email'          : u.email,
            #'postal_address' : u.get_profile().postal_address,
            #'postal_code'    : u.get_profile().postal_code,
            #'postal_city'    : u.get_profile().postal_city,
            #'postal_country' : u.get_profile().postal_country,
            'signed_in'      : True,
            'form'           : form,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))
    # if no session, use a standard context
    else:
        t = loader.get_template('index.html')
        context = Context({ })
        return HttpResponse(t.render(context))


##
# Save the user's profile.
def save_profile(request):
    t = loader.get_template('index.html')
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        t = loader.get_template('profile.html')
        context = Context({
            'username'       : request.POST['user'],
            'fname'          : request.POST['fname'],
            'sname'          : request.POST['sname'],
            'email'          : request.POST['email'],
            'email2'         : request.POST['email2'],
            'passwd'         : request.POST['passwd'],
            'pass2'          : request.POST['pass2'],
            'user_exists'    : True,
            'form'           : form
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))

        # save also avatar picture, if available
        if form.is_valid():
            handle_uploaded_profile_pic(request.FILES['picture'], request.POST['user'] + '.jpg')
        
        # save all the data from the POST into the database
        context = Context({
            'signed_in' : True,
            'user'      : request.POST['user'],
        })
        u = User(
            username       = request.POST['user'],
            first_name     = request.POST['fname'],
            last_name      = request.POST['sname'],
            email          = request.POST['email'],
            password       = hashlib.sha1(request.POST['passwd']).hexdigest(),
        )
        u.save()

        # redirect the user to the home page (already logged-in)
        context.update(csrf(request))
        return HttpResponse(t.render(context))
  

##
# Show a 'foo' page telling that your password has been sent to your email.
def forgot_password(request):
        t = loader.get_template('forgot_password.html')
        context = Context({ })
        return HttpResponse(t.render(context))


##
# Handle an uploaded file.
#
# This function does not only save a file but also do other checks (e.g. picture
# size and resolution). TODO: this is not yet implemented!
#
# @param f File to be handled.
# @param n Name of the file.
def handle_uploaded_profile_pic(f, n):
    fo = open('web/static/images/users/' + n, 'wb+')
    for chunk in f.chunks():
        fo.write(chunk)
    fo.close()
