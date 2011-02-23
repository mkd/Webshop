### necessary Django modules ###
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import *
from django.template import Context, RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

import os.path
PROJECT_DIR = os.path.dirname(__file__)
SID = 'keyforme'
KEY = '8c0593199894c8135c13bf15a31240ad'



### necessary models (other than Django's) ###
from models import *
from forms import *
import datetime, hashlib, os
 

### plain web pages ###
##
# Render the home page. 
def index(request):
    t = loader.get_template('index.html')
    categories = Category.objects.all()
    best_products = Product.objects.filter(stock_count__gt=0).order_by('-average_rating')[:10]
    
    if request.user.is_authenticated():
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'categories'  : categories,
            'products'    : best_products,
            'products_in_cart' : no_items,
        })
    
    else:
        context = Context({
            'categories'  : categories,
            'products'    : best_products,
        })
        
    # render the home page
    context.update(csrf(request))
    return HttpResponse(t.render(context))



##
# Render the user cart page.    
def cart(request):
    if request.user.is_authenticated():
        template = loader.get_template('cart.html')
        user = request.user
        userProducts = CartProduct.objects.filter(user=user)
        
        total = 0
        for product in userProducts:
            total += product.quantity * product.product.price
            
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : no_items,
            'cart'  : userProducts,
            'total' : total,
        })
        
        context.update(csrf(request))
        return HttpResponse(template.render(context))
    
    else:
        t = loader.get_template('index.html')
        context = Context({ })
        return HttpResponse(t.render(context))


##
# TODO: document me!        
def myProducts(request, payment_id):
    if request.user.is_authenticated():
        template = loader.get_template('myProducts.html')
        payment = get_object_or_404(Payment, id=payment_id) 
        
        if payment.user != request.user:
            return HttpResponseRedirect("/")
        
        products = Transaction.objects.filter(payment=payment)          
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : no_items,
            'payment'  : payment,
            'products'  : products,
            'message'   : request.GET.get('m',''),
        })
        return HttpResponse(template.render(context))
        
    else:
        return HttpResponseRedirect("/")
   

##
# TODO: document me! 
def myTransactions(request):
    if request.user.is_authenticated():
        template = loader.get_template('transactions.html')
        payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : no_items,
            'payments'  : payments,
            'message'   : request.GET.get('m',''),
        })
        return HttpResponse(template.render(context))
        
    else:
        return HttpResponseRedirect("/")

##
# TODO: document me!
def addToCart(request):
    if request.user.is_authenticated():
        profile = get_object_or_404(UserProfile, user=request.user) 
        profile.products_in_cart += 1
        profile.save()
        product = get_object_or_404(Product, id=request.POST['product'])

        try: 
            new_prod = CartProduct.objects.get(product=product, user=request.user)
            new_prod.quantity += 1
        
        except CartProduct.DoesNotExist: 
            new_prod = CartProduct(product = product, 
                              user = request.user,
                              timestamp = datetime.datetime.now(),
                              quantity = 1)
        
        new_prod.save()
        product.save()
        return HttpResponse("%s" % profile.products_in_cart)
        
    else:
        return HttpResponse("No registered")
        

def deleteFromCart(request):
    if request.method == 'POST':
        prod = get_object_or_404(CartProduct, id=request.POST['product'])
        profile = get_object_or_404(UserProfile, user=request.user) 
        profile.products_in_cart -= prod.quantity
        profile.save()
        prod.delete()
        return HttpResponse(profile.products_in_cart)
    else:
        return HttpResponseRedirect("/")
        
def editQuantityInCart(request):
    if request.method == 'POST':
        prod = get_object_or_404(CartProduct, id=request.POST['product'])
        profile = get_object_or_404(UserProfile, user=request.user) 
        
        if prod.quantity > request.POST['quantity']:
            profile.products_in_cart -= prod.quantity - int(request.POST['quantity'])
        else:
            profile.products_in_cart += int(request.POST['quantity']) - prod.quantity
         
        prod.quantity = int(request.POST['quantity'])
        profile.save()
        prod.save()
        return HttpResponse(profile.products_in_cart)
    else:
        return HttpResponseRedirect("/")
        
def checkout(request):
    if request.user.is_authenticated():
        template = loader.get_template('payment.html')
        products = CartProduct.objects.filter(user=request.user)
    
        prices = []
        total = 0
        for product in products:
            thisProd = get_object_or_404(Product, id=product.product.id)
            product.total = product.quantity * thisProd.price
            total += product.total
            
        payment = Payment( user=request.user, amount=total)
        payment.pid = "%d-%s" % (request.user.id, datetime.datetime.now())
        checksumstr = "pid=%s&sid=%s&amount=%s&token=%s" % (payment.pid, SID, payment.amount, KEY)
        m = md5.new(checksumstr)
        payment.checksum = m.hexdigest()
        payment.save()
    
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : no_items,
            'sid'     : SID,
            'cost'    : prices,
            'cart'    : products,
            'payment' : payment,
        })
    
        context.update(csrf(request))
        return HttpResponse(template.render(context))
    
    else:
        return HttpResponseRedirect("/")
       

##
# TODO: document me! 
def paymentOk(request):
    if request.user.is_authenticated():
        pid = request.GET.get('pid')
        ref = request.GET.get('ref')
        checksum = request.GET.get('checksum')
        
        checksumstr = "pid=%s&ref=%s&token=%s" % (pid, ref, KEY)
        m = md5.new(checksumstr)
        myChecksum = m.hexdigest()
        
        print myChecksum
        print checksum
        
        if checksum == myChecksum:
            user = request.user
            payment = get_object_or_404(Payment, pid=pid)
            payment.ref = ref
            payment.save()
            products = CartProduct.objects.filter(user=user)
            
            for product in products:
                transaction = Transaction( 
                    product = product.product,
                    user = user,
                    payment = payment,
                    quantity = product.quantity,
                    unit_price = product.product.price)
                
                theProduct = product.product
                theProduct.stock_count -= product.quantity
                theProduct.sold_count += product.quantity
                theProduct.save()
                transaction.save()
                product.delete()
            
            profile = get_object_or_404(UserProfile, user=user) 
            profile.products_in_cart = 0
            profile.save()
            
            return HttpResponseRedirect("/myTransactions?m=Payment succesful!")
            
        else:
            payment = get_object_or_404(Payment, pid=pid)
            payment.delete()
            return HttpResponseRedirect("/checkout")

##
# TODO: document me!    
def paymentNo(request):
    payment = get_object_or_404(Payment, pid=pid)
    payment.delete()
    return HttpResponseRedirect("/checkout")


##
# Ask the user for the master password, in order to enter the administrative
# pages.
def myadmin(request):
    # if the user is authenticated and is staff, go straight to the admin page
    if request.user.is_authenticated() and request.user.is_staff:
        t = loader.get_template('myadmin_page.html')
        context = RequestContext(request, { })
        return HttpResponse(t.render(context))

    # if the user is not logged in, ask for master password
    else:
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
        path = PROJECT_DIR + '/static/master.passwd'
        f = open(path, 'r')
        masterpass = f.readline().rstrip()
        f.close()
        # if passwords match, enter the administrative page
        if hashlib.sha1(request.POST.get(['pass'])).hexdigest() == masterpass:
            authenticate(username='root', password=request.POST.get(['pass']))
            t = loader.get_template('myadmin_page.html')
            context = RequestContext(request, {
                'login_failed' : False,
            })
            
        # if passwords do not match, go back and place an error
        else:
            t = loader.get_template('myadmin.html')
            context = RequestContext(request, {
                'login_failed' : True,
            })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Render the products administration page.
def myadmin_products(request):
    products = Product.objects.all()
    t = loader.get_template('myadmin_products.html')
    context = RequestContext(request, {
        'products'    : products,
        'products_no' : len(products),
    })
    return HttpResponse(t.render(context))


##
# Render a page to add a new product.
def myadmin_addProduct(request):
    form = AddProductForm(request.POST)
    t = loader.get_template('myadmin_add_product.html')
    context = RequestContext(request, {
        'form': form,
    })
    context.update(csrf(request))
    return HttpResponse(t.render(context))

##
# Add a product to the database.
def addProduct(request):
    if request.method == 'POST':
        # save all the data from the POST into the database
        p = Product.objects.create(
            name            = request.POST.get('name'),
            description     = request.POST('desc'),
            price           = request.POST('price'),
            stock_count     = request.POST('units'),
            #tags           = request.POST['tags'],
        )
        p.save()

        # save icon
        handleUploadedPic('products', request.FILES.get('picture'), str(p.id))

        # redirect the products management page
        t = loader.get_template('myadmin_products.html')
        context = RequestContext(request, {
            'product_added' : True,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Render a page to edit a product.
def editProduct(request, product_id):
    t = loader.get_template('myadmin_edit_product.html')
    p = Product.objects.get(id=product_id)
    data = {
        'name'        : p.name,
        'desc'        : p.description,
        'units'       : p.stock_count,
        'price'       : p.price,
    }
    form = EditProductForm(data)
#    forms.fields['category'].initial = 1

    # load unknown avatar if no profile picture
    pic = 'web/static/images/products/' + str(product_id)
    if not os.path.exists(pic):
        pic = 'static/images/products/unknown.png'
    else:
        pic = 'static/images/products/' + str(product_id)

    context = RequestContext(request, {
        'icon' : pic,
        'form' : form,
        'product_id' : product_id,
    })
    return HttpResponse(t.render(context))


##
# Save a modified product.
def saveProduct(request, product_id):
    t = loader.get_template('myadmin_edit_product.html')
    if request.method == 'POST':
        # save all the data from the POST into the database
        p = Product.objects.get(id=product_id)
        p.name          = request.POST.get('name')
        p.description   = request.POST.get('desc')
        p.category_id   = request.POST.get('category', 0)
        p.stock_count   = request.POST.get('units', 0)
        p.price         = request.POST.get('price', 0)
        p.save()

        # save the icon, if available
        handleUploadedPic('products', request.FILES.get('picture'), str(p.id))

        # display editProduct again
        data = {
            'name'        : p.name,
            'desc'        : p.description,
            'category'    : p.category_id,
            'units'       : p.stock_count,
            'price'       : p.price,
        }
        form = EditProductForm(data)

        # load unknown avatar if no profile picture
        pic = 'web/static/images/products/' + str(p.id)
        if not os.path.exists(pic):
            pic = 'static/images/products/unknown.png'
        else:
            pic = 'static/images/products/' + str(p.id)
        
        # redirect the user to the home page (already logged-in)
        form = EditProductForm(data)
        context = RequestContext(request, {
            'icon'          : pic,
            'form'          : form,
            'product_name'  : p.name,
            'product_saved' : True,
            'product_id'    : product_id,
        })

    # render response
    context.update(csrf(request))
    return HttpResponse(t.render(context))
   
    
##
# Render a specific product page.    
def product(request, product_id):
    template = loader.get_template('product.html')   
    product = get_object_or_404(Product, id=product_id)
    comments = Comment.objects.filter(product=product_id).order_by('timestamp')
   
    # TODO: document me!
    if request.user.is_authenticated():
        form = CommentForm()
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'product'           : product,
            'comments'          : comments,
            'form'              : form,
            'products_in_cart'  : no_items,
        })
        
    # TODO: document me!    
    else:
        context = RequestContext(request, {
            'product'  : product,
            'comments' : comments,
        })
   
    # increment the number of visits to the product 
    product.visit_count +=1;
    product.save()

    context.update(csrf(request))
    return HttpResponse(template.render(context))


##
# Set a rating for a given product.
def rateProduct(request):
    if request.user.is_authenticated() and request.method == 'POST':
        element = request.POST.get('product')
        rate    = request.POST.get('rate')
       
        # TODO: document me! 
        prodTransaction = Transaction.objects.get(user=request.user, id=element)  
        product = Product.objects.get(id=prodTransaction.product.id)
       
        # TODO: document me! 
        if prodTransaction.rate == 0:
            product.votes += 1
            product.points += int(rate)
       
        # TODO: document me! 
        else:
            product.points -= prodTransaction.rate
            product.points += int(rate)
        
        prodTransaction.rate = int(rate)
        prodTransaction.save()
        product.save()
        return HttpResponse(rate)
       
    # TODO: document me! 
    else:
        return HttpResponseRedirect("/checkout")


##
# Render the categories administration page.
# TODO: this is just a copy paste from products
def myadmin_categories(request):
    return HttpResponseRedirect('/admin/web/category/')


##
# Render the orders administration page.
def myadmin_orders(request):
    orders = Transaction.objects.all()
    t = loader.get_template('myadmin_orders.html')
    context = RequestContext(request, {
        'orders'    : orders,
        'orders_no' : len(orders),
    })
    return HttpResponse(t.render(context))


##
# Render the users administration page.
def myadmin_users(request):
    return HttpResponseRedirect('/admin/auth/user')



### comments functionality ###
##
# Publish a comment on a page 
def comment(request, product_id):
    template = loader.get_template('product.html')
   
    # TODO: document me! 
    if request.method == 'POST':
        form = CommentForm(request.POST)
       
        # TODO: document me! 
        if form.is_valid() and request.user.is_authenticated():
            product = get_object_or_404(Product, id=product_id)
            user    = request.user
            text    = form.cleaned_data['comment']         
            reply   = request.POST.get('in_reply')
            product.comment_count += 1
      
            # TODO: document me!      
            if reply != '0':
                reply = Comment.objects.get(id=reply)
                new_comment = Comment(
                    product = product, 
                    user = user,
                    timestamp = datetime.datetime.now(),
                    comment = text,
                    parent_id = reply
                )

            # TODO: document me!
            else:
                new_comment   = Comment(
                    product   = product, 
                    user      = user,
                    timestamp = datetime.datetime.now(),
                    comment   = text
                    )
   
            # TODO: document me! 
            new_comment.save()
            product.save()
            comments = Comment.objects.filter(product=product_id).order_by('timestamp')
    
    return HttpResponseRedirect('/product/%s' % (product_id))        


##
# Rate a comment for a product.
def rateComment(request, comment_id, option): 
    template = loader.get_template('product.html')
    comment = get_object_or_404(Comment, id=comment_id)
   
    # TODO: document me 
    if option == '1':
        comment.positives += 1
    else:
        comment.negatives -= 1
    
    comment.save()

    # TODO: clean up!
    return HttpResponse("<a onclick=\"showReplyBox('%s');\">Reply</a> | %s <img src=\"/static/images/up.png\" /> &nbsp;<img src=\"/static/images/down.png\" /> %s" % (comment.id, comment.positives, comment.negatives))



### products pages ###
##
# Render a page with all the products of a specific category. 
def category(request, category_id):
    template = loader.get_template('list.html')
    thisCategory = get_object_or_404(Category, id=category_id)  
    categories = Category.objects.all()
    best_products = Product.objects.filter(category=thisCategory.id).filter(stock_count__gt=0).order_by('-average_rating')[:10]
    message = "Products on " + thisCategory.name
   
    # TODO: document me! 
    if request.user.is_authenticated():
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'message'           : message,
            'categories'        : categories,
            'products'          : best_products,
            'products_in_cart'  : no_items,
        })

    # TODO: document me!
    else:
        context = RequestContext(request, {
            'message'           : message,
            'this'              : thisCategory,
            'categories'        : categories,
            'products'          : best_products,
        })
    
    context.update(csrf(request))
    return HttpResponse(template.render(context))

 
##
# Search for a product.
def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
       
        # TODO: document me! 
        if form.is_valid():
            query = form.cleaned_data['query']
           
            try: 
                products = Product.objects.filter(name__icontains = query)
            except Product.DoesNotExist: 
                # TODO: redirect to a good-looking page!
                return HttpResponse("Sorry, we couldn't find your product.")
           
            categories = Category.objects.all()            
            template = loader.get_template('list.html')
            message = "Search results for %s." % query
         
            # TODO: document me! 
            if request.user.is_authenticated():
                no_items = request.user.get_profile().products_in_cart
                context = RequestContext(request, {
                    'message'           : message,
                    'categories'        : categories,
                    'products'          : products,
                    'products_in_cart'  : no_items,
                })

            # TODO: document me!
            else:
                context = RequestContext(request, {
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
    t = loader.get_template('signup.html')
    form = RegisterForm()
    categories = Category.objects.all()
    context = RequestContext(request,
    {
        'form'       : form,
        'categories' : categories,
    })
    return HttpResponse(t.render(context))


##
# Render a simple login form (sign in)
def signin(request):
    t = loader.get_template('signin.html')
    categories = Category.objects.all()
    context = RequestContext(request, { 
        'categories' : categories,
    })
    return HttpResponse(t.render(context))


##
# Perform the actual login.
#
# This function checks the user and password against the users in the database
# and tries to log in. If successful, the user is redirected to the home page,
# otherwise an error is displayed.
def tryLogin(request):
    # authenticate the user
    username = request.POST.get('user')
    password = request.POST.get('pass')
    user = authenticate(username=username, password=password)

    # on sign-in go to front-page, otherwise go back to sign-in form
    if user is not None:
        login(request, user)
        return HttpResponseRedirect('/')
    else:
        t = loader.get_template('signin.html')
        categories = Category.objects.all()
        context = RequestContext(request, {
            'login_failed' : True,
            'categories'   : categories,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Close the session for an user and go to the front page.
def signout(request):
    logout(request)
    return HttpResponseRedirect('/')  


##
# Add a new user.
def register(request):
    t = loader.get_template('signin.html')
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        # server-side validation
        if form.is_valid():
            # check if the user already exists in the database
            try:
                check_username = User.objects.get(username=request.POST.get('user'))
            except:
                check_username = None
            try:
                check_email = User.objects.get(email=request.POST.get('email'))
            except:
                check_email = None

            # if the username or email already exist, go back to the sign-up
            # form and remember the entered data
            if check_username is not None or check_email is not None:
                t = loader.get_template('signup.html')
                context = RequestContext(request, {
                    'username'       : request.POST.get('user'),
                    'fname'          : request.POST.get('fname'),
                    'sname'          : request.POST.get('sname'),
                    'email'          : request.POST.get('email'),
                    'email2'         : request.POST.get('email2'),
                    'passwd'         : request.POST.get('passwd'),
                    'pass2'          : request.POST.get('pass2'),
                    'user_exists'    : True,
                    'form'           : form
                })
                context.update(csrf(request))
                return HttpResponse(t.render(context))

            # save all the data from the POST into the database
            u  = User.objects.create_user(
                request.POST.get('user'),
                request.POST.get('email'),
                request.POST.get('passwd')
            )
            up = UserProfile.objects.create(user_id=u.id)
            u.is_staff   = False
            u.first_name = request.POST.get('fname')
            u.last_name  = request.POST.get('sname')
            u.save()
            up.save()

            # save also avatar picture, if available
            handleUploadedPic('users', request.FILES.get('picture'), u.id)

            # redirect the user to the login page with a welcome
            context = RequestContext(request, {
                'user'       : request.POST.get('user'),
                'registered' : True,
            })
            context.update(csrf(request))
            return HttpResponse(t.render(context))


##
# Render the user profile page.
def editProfile(request):
    # check for an existing session
    if request.user.is_authenticated():
        t = loader.get_template('profile.html')
        form = ProfileForm(request.POST, request.FILES)

        # obtain the data from the user and display his/her profile
        u = User.objects.get(id=request.user.id)
        no_items = u.get_profile().products_in_cart

        # load unknown avatar if no profile picture
        pic = 'web/static/images/users/' + str(u.id)
        if not os.path.exists(pic):
            pic = 'static/images/users/new_user.png'
        else:
            pic = 'static/images/users/' + str(u.id)

        # set the rest of the data
        context = RequestContext(request, {
            'picture'          : pic,
            'user'             : u.username,
            'fname'            : u.first_name,
            'sname'            : u.last_name,
            'email'            : u.email,
            'products_in_cart' : no_items,
            'address'          : u.get_profile().postal_address,
            'postal_code'      : u.get_profile().postal_code,
            'city'             : u.get_profile().postal_city,
            'country'          : u.get_profile().postal_country,
            'form'             : form,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))
    # if no session, use a standard context
    else:
        return HttpResponseRedirect('/')


##
# Save the user's profile.
def saveProfile(request):
    t = loader.get_template('profile.html')
    if request.method == 'POST':
        # save all the data from the POST into the database
        up = UserProfile.objects.get(user=request.user.id)
        u = User.objects.get(id=request.user.id)
        u.first_name = request.POST.get('fname')
        u.last_name  = request.POST.get('sname')
        up.postal_address = request.POST.get('address')
        up.postal_code    = request.POST.get('postal_code')
        up.postal_city    = request.POST.get('city')
        up.postal_country = request.POST.get('country')

        # if pass and pass2 match, save them as the new password
        pwd = request.POST.get('passwd', None)
        if pwd != '' and pwd != None and (pwd == request.POST.get('pass2')):
            u.set_password(pwd)

        # save the avatar picture, if available
        handleUploadedPic('users', request.FILES.get('picture'), str(u.id))

        # commit to the database
        u.save()
        up.save()

        # display profile again
        form = ProfileForm(request.POST, request.FILES)
        context = RequestContext(request, {
            'picture'        : '/static/images/users/' + str(u.id),
            'user'           : u.username,
            'fname'          : u.first_name,
            'sname'          : u.last_name,
            'email'          : u.email,
            'address'        : u.get_profile().postal_address,
            'postal_code'    : u.get_profile().postal_code,
            'city'           : u.get_profile().postal_city,
            'country'        : u.get_profile().postal_country,
            'form'           : form,
            'saved'          : True,
        })

    # redirect the user to the home page (already logged-in)
    context.update(csrf(request))
    return HttpResponse(t.render(context))
  

##
# Show a dummy page telling that your password has been sent to your email.
#
# TODO: implement this template and functionality!
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
# @param d Directory where to store the picture.
# @param f File to be handled.
# @param n Name of the file.
def handleUploadedPic(d, f, n):
    # if no file uploaded, don't change the picture
    if f is None:
        return

    # if a file is provided, then save it where it belongs
    fo = open('web/static/images/' + d + '/' + n, 'wb+')
    for chunk in f.chunks():
        fo.write(chunk)
    fo.close()
    
    
##
# Delete a set of products.
def deleteProducts(request):
    t = loader.get_template('myadmin_products.html')

    # delete products
    # note: comments are not necessarily deleted, because the user miht want to
    # check a comment he or she wrote in the past (even if the product does not
    # exist anymore)
    if request.method == 'POST':
        products = request.POST.getlist('product_list')
        for p in products:
            product = Product.objects.get(pk=p)
            product.delete()
            # also delete the picture of the product
            os.remove('static/images/products/' + str(p.id))

    # return to the products page
    products = Category.objects.all()
    context = RequestContext(request, {
        'categories':  products,
    })
    return HttpResponse(t.render(context))


##
# Delete a set of orders.
def deleteOrders(request):
    t = loader.get_template('myadmin_orders.html')

    # delete categories and set their products orphaned 
    if request.method == 'POST':
        order_list = request.POST.getlist('order_list')
        for oid in order_list:
            o = Transaction.objects.get(pk=oid)
            o.delete()

    orders = Transaction.objects.all()
    context = RequestContext(request, {
        'orders':  orders,
    })
    return HttpResponse(t.render(context))


##
# Render a page to edit a user.
#
# TODO: this is just a copy from editProduct.
def editUser(request, user_id):
    t = loader.get_template('myadmin_edit_user.html')
    u = User.objects.get(id=user_id)
    data = {
        'name'        : u.name,
        'desc'        : u.description,
        'units'       : u.stock_count,
        'price'       : u.price,
    }
    form = EditUserForm(data)
    form.fields['category'].initial = p.category

    # load unknown avatar if no profile picture
    pic = 'web/static/images/products/' + str(product_id)
    if not os.path.exists(pic):
        pic = 'static/images/products/unknown.png'
    else:
        pic = 'static/images/products/' + str(product_id)

    context = RequestContext(request, {
        'icon' : pic,
        'form' : form,
        'product_id' : product_id,
    })
    return HttpResponse(t.render(context))
