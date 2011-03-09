### views.py
### This module contains the main views for rendering Webshop.
### (c) 2011 The Webshop team

### necessary libraries ###
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import *
from django.template import Context, RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from login import *
from myadmin import *
from utils import *
from models import *
from forms import *
import datetime, hashlib, os

### project path settings ###
import os.path
PROJECT_DIR = os.path.dirname(__file__)
SID = 'keyforme'
KEY = '8c0593199894c8135c13bf15a31240ad'




##
# Render the home page. 
def index(request):
    t = loader.get_template('index.html')
    
    # load the categories and the products ordered by rating
    categories = Category.objects.all()
    best_products = Product.objects.filter(stock_count__gt=0).order_by('-average_rating')[:10]
    
    context = RequestContext(request, {
        'categories'  : categories,
        'products'    : best_products,
    })
    
    # if the user is authenticated, then send info about the card in the request
    if request.user.is_authenticated():
        number_items_in_cart = request.user.get_profile().products_in_cart
        context.update({'products_in_cart': number_items_in_cart})
    else:
        login_form = LoginForm()
        context.update({'login_form': login_form})
    
    # if show-as-icons option, then send this option to the template
    if request.GET.get('l') == 'icons':
        context.update({'icons': 'OK'})
        
    # render the home page
    context.update(csrf(request))
    return HttpResponse(t.render(context))
    

##
# Render the user cart page.
def cart(request):
    # if user is authenticated then show the products in the user's cart
    if is_auth(request):
        # get the user, the template and any message received by GET
        user = request.user
        template = loader.get_template('cart.html')
        message = request.GET.get('m', '')
        userProducts = CartProduct.objects.filter(user=user)
        
        # calculate the total amount of money spent by the user
        total = 0
        for product in userProducts:
            total += product.quantity * product.product.price
            
        number_items_in_cart = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : number_items_in_cart,
            'cart'   : userProducts,
            'total'  : total,
            'message': message,
        })
        
        context.update(csrf(request))
        return HttpResponse(template.render(context))

    return HttpResponseRedirect('/')


##
# Shows the products that the user pay in a transaction.      
def myProducts(request, payment_id):
    if is_auth(request):
        template = loader.get_template('myProducts.html')
        payment = get_object_or_404(Payment, id=payment_id) 
        
        # check that this transaction is related to this user (security check)
        if payment.user != request.user:
            return HttpResponseRedirect("/")
        
        # retreive all the products and render the page
        products = Transaction.objects.filter(payment=payment)          
        number_items_in_cart = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : number_items_in_cart,
            'payment'  : payment,
            'products'  : products,
            'message'   : request.GET.get('m',''),
        })
        return HttpResponse(template.render(context))

    return HttpResponseRedirect('/')
   

##
# Shows a list of transactions done by a user.
def myTransactions(request):
    if is_auth(request):
        template = loader.get_template('transactions.html')
        payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
        number_items_in_cart = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : number_items_in_cart,
            'payments'  : payments,
            'message'   : request.GET.get('m',''),
        })
        return HttpResponse(template.render(context))

    return HttpResponseRedirect('/')
        

##
# Add a product to the user's cart.
def addToCart(request):
    if is_auth(request):
        # get the user's profile and the product
        profile = get_object_or_404(UserProfile, user=request.user) 
        product = get_object_or_404(Product, id=request.POST['product'])

        # if product already in the cart, then increment the number of products
        try: 
            new_prod = CartProduct.objects.get(product=product, user=request.user)
            new_prod.quantity += 1
        # otherwise add the new product to the cart
        except CartProduct.DoesNotExist: 
            new_prod = CartProduct(product = product, 
                              user = request.user,
                              timestamp = datetime.datetime.now(),
                              quantity = 1)
        
        # increment number of products in user's profile and save the objects
        profile.products_in_cart += 1
        profile.save()
        new_prod.save()
        product.save()
        return HttpResponse("%s" % profile.products_in_cart)

    return HttpResponseRedirect('/')


##
# Remove a product from the user's cart.
def deleteFromCart(request):
    if is_auth(request) and request.method == 'POST':
        prod = get_object_or_404(CartProduct, id=request.POST['product'])
        profile = get_object_or_404(UserProfile, user=request.user) 
        profile.products_in_cart -= prod.quantity
        profile.save()
        prod.delete()
        return HttpResponse(profile.products_in_cart)

    return HttpResponseRedirect('/')


##
# Change the quantity of product in the user's cart.  
def editQuantityInCart(request):
    if is_auth(request) and request.method == 'POST':
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

    return HttpResponseRedirect('/')


##
# Show the payment page of an order, the user see the list of products to buy
#  and the postal address wher the products will be sent.      
def checkout(request):
    if is_auth(request):
        template = loader.get_template('payment.html')
        products = CartProduct.objects.filter(user=request.user)
        message = request.GET.get('m', '')
        prices = []
        total = 0
        
        # calculate the total amount of the order
        for product in products:
            thisProd = get_object_or_404(Product, id=product.product.id)
            product.total = product.quantity * thisProd.price
            total += product.total
        
        # generate the data to send to the bank and the Payment object
        payment = Payment( user=request.user, amount=total)
        payment.pid = "%d-%s" % (request.user.id, datetime.datetime.now())
        checksumstr = "pid=%s&sid=%s&amount=%s&token=%s" % (payment.pid, SID, payment.amount, KEY)
        m = md5.new(checksumstr)
        payment.checksum = m.hexdigest()
        payment.save()
        
        # generate a form to edit the postal information
        profile = request.user.get_profile()
        postal_form = PostalForm(instance=profile)
        number_items_in_cart = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : number_items_in_cart,
            'sid'     : SID,
            'cost'    : prices,
            'cart'    : products,
            'payment' : payment,
            'message' : message,
            'postal_form' : postal_form,
            'profile' : profile,
        })

        context.update(csrf(request))
        return HttpResponse(template.render(context))

    return HttpResponseRedirect('/')
  

##
# If the bank returns an OK response then we store the Payments
# and all the products in the cart lic transactions.
def updatePostalOrder(request):
    if is_auth(request) and request.method == 'POST':
        form = PostalForm(request.POST)
        
        # get the Payment and adds the postal info
        pid =  request.POST.get('pid')       
        payment = get_object_or_404(Payment, pid=pid)
        if request.POST.get('postal_address') != '' and request.POST.get('postal_code') != '' and request.POST.get('postal_city') != '' and request.POST.get('postal_country') != '':
            payment.postal_address = request.POST.get('postal_address')
            payment.postal_code = request.POST.get('postal_code')
            payment.postal_city = request.POST.get('postal_city')
            payment.postal_country = request.POST.get('postal_country')
            payment.save()
            return HttpResponse("OK")
        else:
            return HttpResponse("[ERROR]: You have to to provide postal information.")
    
    return HttpResponse("NO")


##
# If the bank returns an OK response then we store the Payments
# and all the products in the cart lic transactions.
def paymentOk(request):
    if is_auth(request):
        # obtain the data from the GET request
        pid = request.GET.get('pid')
        ref = request.GET.get('ref')
        checksum = request.GET.get('checksum')
        
        # do the checksum
        checksumstr = "pid=%s&ref=%s&token=%s" % (pid, ref, KEY)
        m = md5.new(checksumstr)
        myChecksum = m.hexdigest()
        
        # check that the checksum is correct
        if checksum == myChecksum and ref > 0:
            # Get the Payment and adds the ref.
            payment = get_object_or_404(Payment, pid=pid)
            payment.ref = ref
            payment.save()
            
            # get the products in the user's cart and add them to the transaction
            user = request.user
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
            
            # reset the cart product counter of the user
            profile = get_object_or_404(UserProfile, user=user) 
            profile.products_in_cart = 0
            profile.save()
            
            return HttpResponseRedirect("/myTransactions?m=Payment succesful!")
         
        # if the checksum doesn't validate, then delete the payment
        else:
            payment = get_object_or_404(Payment, pid=pid)
            payment.delete()
            return HttpResponseRedirect("/checkout?m=The checksum does not validate!")

    return HttpResponseRedirect('/')


##
# Handle an canceled payment, triggered when the user cancel the payment in the bank.
def paymentNo(request):
    if is_auth(request):
        # get the values sent by the bank and check that the checksum matches
        pid = request.GET.get('pid')
        ref = request.GET.get('ref')
        checksum = request.GET.get('checksum')
        
        checksumstr = "pid=%s&ref=%s&token=%s" % (pid, ref, KEY)
        m = md5.new(checksumstr)
        myChecksum = m.hexdigest()
        
        # if the checksum matches then delete the payment and returns the user to 
        # the cart page showing a message
        if checksum == myChecksum:
            payment = get_object_or_404(Payment, pid=pid)  
            payment.delete()
            return HttpResponseRedirect("/cart?m=You cancel the payment.")
        else:
            return HttpResponseRedirect("/")

    return HttpResponseRedirect('/')


##
# Handle an error on payment. 
def paymentError(request):
    if is_auth(request):
        # get the values sent by the bank and check that the checksum matches
        pid = request.GET.get('pid')
        ref = request.GET.get('ref')
        checksum = request.GET.get('checksum')

        checksumstr = "pid=%s&ref=%s&token=%s" % (pid, ref, KEY)
        m = md5.new(checksumstr)
        myChecksum = m.hexdigest()
        
        # if the checksum matches then delete the payment and returns the user to 
        # the checkout page showing a message
        if checksum == myChecksum:
            payment = get_object_or_404(Payment, pid=pid)
            payment.delete()
            return HttpResponseRedirect("/checkout?m=Some error occurs while trying to connect to the bank.")
        else:
            return HttpResponseRedirect("/")

    return HttpResponseRedirect('/')


##
# Render a specific product page.    
def product(request, product_id):
    # get the template and try to get the product, if not it thow a 404 error
    template = loader.get_template('product.html')   
    product = get_object_or_404(Product, id=product_id)
    comments = Comment.objects.filter(product=product_id).order_by('timestamp')
   
    context = RequestContext(request, {
        'product'  : product,
        'comments' : comments,
    })
   
    # If the user is logged then get the products in the user's cart and show the comment form.
    if request.user.is_authenticated():
        comment_form = CommentForm()
        number_items_in_cart = request.user.get_profile().products_in_cart
        context.update({
            'form'              : comment_form,
            'products_in_cart'  : number_items_in_cart,
        })
    
    # If the user is not logged then get the login form and show it.        
    else:
        login_form = LoginForm()
        context.update({'login_form': login_form})
   
    # increment the number of visits to the product 
    product.visit_count +=1;
    product.save()

    context.update(csrf(request))
    return HttpResponse(template.render(context))


##
# Set a rating for a given product.
def rateProduct(request):
    if is_auth(request) and request.method == 'POST':
        element = request.POST.get('product')
        rate    = request.POST.get('rate')
       
        # get the product from the transaction list of products of the user
        prodTransaction = Transaction.objects.get(user=request.user, id=element)  
        product = Product.objects.get(id=prodTransaction.product.id)
       
        # if the user already receive the product in his home
        if prodTransaction.payment.status == "Delivered":
            # if the user did not rate the product before
            if prodTransaction.rate == 0:
                product.votes += 1
                product.points += int(rate)             
            else:
                product.points -= prodTransaction.rate
                product.points += int(rate)
        
        prodTransaction.rate = int(rate)
        prodTransaction.save()
        product.save()
        return HttpResponse(rate)
    else:
        return HttpResponseRedirect("/checkout")

    return HttpResponseRedirect('/')


### comments functionality ###
##
# Publish a comment on a page 
def comment(request, product_id):
    template = loader.get_template('product.html')

    if is_auth(request) and request.method == 'POST':
        form = CommentForm(request.POST)
       
        # if the form is valid
        if form.is_valid():
            product = get_object_or_404(Product, id=product_id)
            user    = request.user
            text    = form.cleaned_data['comment']         
            reply   = request.POST.get('in_reply')
            product.comment_count += 1
      
            # if the comment is areply to other comment
            if reply != '0':
                reply = Comment.objects.get(id=reply)
                new_comment = Comment(
                    product = product, 
                    user = user,
                    timestamp = datetime.datetime.now(),
                    comment = text,
                    parent_id = reply
                )

            else:
                new_comment   = Comment(
                    product   = product, 
                    user      = user,
                    timestamp = datetime.datetime.now(),
                    comment   = text
                    )
   
            # save the changes on the product ant the comment, and render the product page again.
            new_comment.save()
            product.save()
            comments = Comment.objects.filter(product=product_id).order_by('timestamp')
    
    return HttpResponseRedirect('/product/%s' % (product_id))        


##
# Rate a comment for a product.
def rateComment(request, comment_id, option): 
    if is_auth(request):
        template = loader.get_template('product.html')
        comment = get_object_or_404(Comment, id=comment_id)
       
        if option == '1':
            comment.positives += 1
        else:
            comment.negatives -= 1
        
        comment.save()

        # sent by AJAX the new number of votes
        return HttpResponse("<a onclick=\"showReplyBox('%s');\">Reply</a> | %s <img src=\"/static/images/up.png\" /> &nbsp;<img src=\"/static/images/down.png\" /> %s" % (comment.id, comment.positives, comment.negatives))

    return HttpResponseRedirect('/')



### products pages ###
##
# Render a page with all the products of a specific category. 
def category(request, category_id):
    # load the category and the products in the category ordered by rate
    template = loader.get_template('list.html')
    thisCategory = get_object_or_404(Category, id=category_id)  
    categories = Category.objects.all()
    best_products = Product.objects.filter(category=thisCategory.id).filter(stock_count__gt=0).order_by('-average_rating')[:10]
    message = "Products on " + thisCategory.name
   
   # generate a base context
    context = RequestContext(request, {
        'message'           : message,
        'this'              : thisCategory,
        'categories'        : categories,
        'products'          : best_products,
    })
   
    # if the user is logged, send the products in the cart to the context 
    if request.user.is_authenticated():
        number_items_in_cart = request.user.get_profile().products_in_cart
        context.update({'products_in_cart'  : number_items_in_cart})
    else:
        login_form = LoginForm()
        context.update({'login_form': login_form})

    # if receives the option to show as icons the send this option to the template
    if request.GET.get('l') == 'icons':
        context.update({'icons': 'OK'})
    
    context.update(csrf(request))
    return HttpResponse(template.render(context))

 
##
# Search for a product.
def search(request):
    # if get a query thorugh GET
    if request.method == 'GET':
        form = SearchForm(request.GET)
        
        if form.is_valid():
            template = loader.get_template('list.html')
            # get clean information of the query
            query = form.cleaned_data['query']
            categories = Category.objects.all()
            
            context = RequestContext(request, {
                'categories'  : categories,
                'query'       : request.GET.get('query'),
            })
           
            # if the user is authenticated then show the number of products in their cart
            if request.user.is_authenticated():
                number_items_in_cart = request.user.get_profile().products_in_cart
                context.update({ 'products_in_cart'  : number_items_in_cart })
            # if not the login form
            else:
                login_form = LoginForm()
                context.update({ 'login_form': login_form })
                
            # Try to get the products that validate the query.
            db_query = """SELECT DISTINCT web_product.* 
                            FROM web_product, web_category 
                            WHERE 
                                web_product.name like '%%%%%s%%%%' or
                                web_product.description like '%%%%%s%%%%' or
                                (
                                    web_product.category_id = web_category.id and 
                                    web_category.name like '%%%%%s%%%%'
                                )
                            """ % (query,query,query)
                            
            products = Product.objects.raw(db_query)
                
            if len(list(products)) > 0:
                message = "Search results for \"%s\"." % query
                context.update({ 
                    'products'  : products,
                    'message'  : message,
                 })
                 
                if request.GET.get('l') == 'icons':
                    context.update({'icons': 'OK'})
                    
            # if the query does not return products
            else:
                message = "Sorry, we couldn't find your product for \"%s\"." % query
                context.update({ 'message'  : message })
                
            context.update(csrf(request))
            return HttpResponse(template.render(context))
           
    return HttpResponseRedirect('/')
