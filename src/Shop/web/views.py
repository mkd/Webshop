### necessary Django modules ###
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from django.template import Context, RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User



### necessary models (other than Django's) ###
from models import Category, Product, Comment, User, UserProfile, CartProduct
from forms import *
import datetime, hashlib, os
 


### plain web pages ###
##
# Render the home page. 
def index(request):
    t = loader.get_template('index.html')
    categories = Category.objects.all()
    best_products = Product.objects.filter(stock_count__gt=0).order_by('-average_rating')[:10]
    searchForm = SearchForm()
    
    context = Context({
        'categories'  : categories,
        'products'    : best_products,
        'form'        : searchForm,
    })

    # render the home page
    context.update(csrf(request))
    return HttpResponse(t.render(context))


##
# Ask the user for the master password, in order to enter the administrative
# pages.
def myadmin(request):
    t = loader.get_template('myadmin.html')
    form = AdminForm(request.POST)
    context = RequestContext(request, {
        'form' : form
    })
    return HttpResponse(t.render(context))


##
# Render the administrative page, after the master password has been entered
# correctly.
def myadmin_page(request):
    if request.method == 'POST':
        f = open('web/master.passwd', 'r')
        masterpass = f.readline().rstrip()
        f.close()
        # if passwords match, enter the administrative page
        if hashlib.sha1(request.POST['pass']).hexdigest() == masterpass:
            # FIXME: these session variables are not stored!
            request.session['id'] = -1
            request.session['user'] = 'superuser'
            t = loader.get_template('myadmin_page.html')
            context = Context({
                'login_failed' : False,
            })
        # if passwords do not match, go back and place an error
        else:
            t = loader.get_template('myadmin.html')
            context = Context({
                'login_failed' : True,
            })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Render the products administration page.
def myadmin_products(request):
    products = Product.objects.all()
    t = loader.get_template('myadmin_products.html')
    context = Context({
        'products'    : products,
        'products_no' : len(products),
    })
    return HttpResponse(t.render(context))


##
# Render a page to add a new product.
def myadmin_add_product(request):
    form = AddProductForm(request.POST)
    t = loader.get_template('myadmin_add_product.html')
    context = Context({
        'form': form,
    })
    return HttpResponse(t.render(context))


##
# Render a page to edit a product.
# TODO: this is juast a copy paste from add product.
def edit_product(request):
    form = AddProductForm(request.POST)
    t = loader.get_template('myadmin_add_product.html')
    context = Context({
        'form': form,
    })
    return HttpResponse(t.render(context))
   
    
##
# Render a specific product page.    
def product(request, product_id):
    template = loader.get_template('product.html')   
    product = get_object_or_404(Product, id=product_id)
    comments = Comment.objects.filter(product=product_id).order_by('timestamp')
    form = CommentForm()
   
    # increment the number of visits to the product 
    product.visit_count +=1;
    product.save()
   
    # show the product view 
    context = Context({
        'product'  : product,
        'comments' : comments,
        'form'     : form,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))


##
# Render the categories administration page.
# TODO: this is just a copy paste from products
def myadmin_categories(request):
    products = Product.objects.all()
    t = loader.get_template('myadmin_products.html')
    context = Context({
        'products'    : products,
        'products_no' : len(products),
    })
    return HttpResponse(t.render(context))


##
# Render a page to add a new category.
# TODO: this is juast a copy paste from add product.
def myadmin_add_category(request):
    form = AddProductForm(request.POST)
    t = loader.get_template('myadmin_add_product.html')
    context = Context({
        'form': form,
    })
    return HttpResponse(t.render(context))


##
# Render a page to edit a category.
# TODO: this is juast a copy paste from add product.
def edit_category(request):
    form = AddProductForm(request.POST)
    t = loader.get_template('myadmin_add_product.html')
    context = Context({
        'form': form,
    })
    return HttpResponse(t.render(context))



##
# Render the orders administration page.
# TODO: this is just a copy paste from products
def myadmin_orders(request):
    products = Product.objects.all()
    t = loader.get_template('myadmin_products.html')
    context = Context({
        'products'    : products,
        'products_no' : len(products),
    })
    return HttpResponse(t.render(context))


##
# Render a page to add a new order.
# TODO: this is juast a copy paste from add product.
def myadmin_add_order(request):
    form = AddProductForm(request.POST)
    t = loader.get_template('myadmin_add_product.html')
    context = Context({
        'form': form,
    })
    return HttpResponse(t.render(context))


##
# Render a page to edit an order.
# TODO: this is juast a copy paste from add product.
def edit_order(request):
    form = AddProductForm(request.POST)
    t = loader.get_template('myadmin_add_product.html')
    context = Context({
        'form': form,
    })
    return HttpResponse(t.render(context))


##
# Render the users administration page.
# TODO: this is just a copy paste from products
def myadmin_users(request):
    products = Product.objects.all()
    t = loader.get_template('myadmin_products.html')
    context = Context({
        'products'    : products,
        'products_no' : len(products),
    })
    return HttpResponse(t.render(context))


##
# Render a page to add a new user.
# TODO: this is juast a copy paste from add product.
def myadmin_add_user(request):
    form = AddProductForm(request.POST)
    t = loader.get_template('myadmin_add_product.html')
    context = Context({
        'form': form,
    })
    return HttpResponse(t.render(context))


##
# Render a page to edit a user.
# TODO: this is juast a copy paste from add product.
def edit_user(request):
    form = AddProductForm(request.POST)
    t = loader.get_template('myadmin_add_product.html')
    context = Context({
        'form': form,
    })
    return HttpResponse(t.render(context))


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



### comments functionality ###
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


##
# Rate a comment for a product.
def rateComment(request, comment_id, option): 
    template = loader.get_template('product.html')
    comment = get_object_or_404(Comment, id=comment_id)
    
    if (option == '1'):
        comment.positives += 1
    else:
        comment.negatives -= 1
    
    comment.save()
    return HttpResponse("<a onclick=\"showReplyBox('%s');\">Reply</a> | %s <img src=\"/static/images/up.png\" /> &nbsp;<img src=\"/static/images/down.png\" /> %s" % (comment.id, comment.positives, comment.negatives))



### products pages ###
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

 
##
# Search for a product.
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



### user registration and session signing ###
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
        request.session['id']   = u.id
        request.session['user'] = u.username
        t = loader.get_template('index.html')
        context = Context({
            'user': request.POST['user'],
            'pass': request.POST['pass'],
            'stored_pass': u.password,
            'login_failed' : False,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))
    # login failed
    else:
        t = loader.get_template('signin.html')
        context = Context({
            'user': None,
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



### extra functionality ###
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
    
    
##
# Render add categry page (sign up)
def render_new_category(request):
    template = loader.get_template('categoryNew.html')
    category = Category()
    form = NewCategoryForm()

    context = Context({
        'category':  category,
        'categoryForm': form,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))


##
# Render list categry page (sign up)
def render_list_category(request):
    template = loader.get_template('categoryList.html')
    categories = Category.objects.all()
    
    context = RequestContext(request, {
        'categories':  categories,
    })
    return HttpResponse(template.render(context))

       
##
# Add a new category.
def insert_category(request):
    template = loader.get_template('categoryNew.html')
    
    if request.method == 'POST':
        form = NewCategoryForm(request.POST)
        
        if form.is_valid():
            new_category = Category(
                name           = request.POST['name'],
                description    = request.POST['description'],
                icon           = request.POST['icon']
            )
            
            new_category.save()
            
    category = Category()
    form = NewCategoryForm()

    context = Context({
        'category':  category,
        'categoryForm': form,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))

##
# delete selected categories
def delete_selected_categories(request):
    template = loader.get_template('categoryList.html')
    
    if request.method == 'POST':
        category_list   = request.POST['categoryList']
        for category_id in category_list:
            category = Category.objects.get(pk=category_id)
            category.delete()

    categories = Category.objects.all()
    context = RequestContext(request, {
        'categories':  categories,
    })
    return HttpResponse(template.render(context))
