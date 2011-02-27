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
        no_items = request.user.get_profile().products_in_cart
        context.update({'products_in_cart': no_items})
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
    if is_auth(request):
        # TODO: document me!
        template = loader.get_template('cart.html')
        message = request.GET.get('m', '')
        user = request.user
        userProducts = CartProduct.objects.filter(user=user)
        
        total = 0
        for product in userProducts:
            total += product.quantity * product.product.price
            
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : no_items,
            'cart'   : userProducts,
            'total'  : total,
            'message': message,
        })
        
        context.update(csrf(request))
        return HttpResponse(template.render(context))


##
# TODO: document me!        
def myProducts(request, payment_id):
    if is_auth(request):
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
   

##
# TODO: document me! 
def myTransactions(request):
    if is_auth(request):
        template = loader.get_template('transactions.html')
        payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : no_items,
            'payments'  : payments,
            'message'   : request.GET.get('m',''),
        })
        return HttpResponse(template.render(context))
        

##
# TODO: document me!
def addToCart(request):
    if is_auth(request):
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


##
# TODO: document me!
def deleteFromCart(request):
    if is_auth(request) and request.method == 'POST':
        prod = get_object_or_404(CartProduct, id=request.POST['product'])
        profile = get_object_or_404(UserProfile, user=request.user) 
        profile.products_in_cart -= prod.quantity
        profile.save()
        prod.delete()
        return HttpResponse(profile.products_in_cart)


##
# TODO: document me!        
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
        no_items = request.user.get_profile().products_in_cart
        context = RequestContext(request, {
            'products_in_cart' : no_items,
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
  

##
# If the bank returns an OK response then we store the Payments
# and all the products in the cart lic transactions.
def updatePostalOrder(request):
    if is_auth(request) and request.method == 'POST':
        pid =  request.POST.get('pid')
        postal_address = request.POST.get('postal_address','')
        postal_code = request.POST.get('postal_code','')
        postal_city = request.POST.get('postal_city','')
        postal_country = request.POST.get('postal_country','')
        
        # Get the Payment and adds the postal info.
        payment = get_object_or_404(Payment, pid=pid)
        payment.postal_address = postal_address
        payment.postal_code = postal_code
        payment.postal_city = postal_city
        payment.postal_country = postal_country
        payment.save()
        return HttpResponse("OK")
    else:
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
    if is_auth(request) and request.method == 'POST':
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


### comments functionality ###
##
# Publish a comment on a page 
def comment(request, product_id):
    template = loader.get_template('product.html')

    if is_auth(request) and request.method == 'POST':
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
    if is_auth(request):
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
        no_items = request.user.get_profile().products_in_cart
        context.update({'products_in_cart'  : no_items})

    # if receives the option to show as icons the send this option to the template
    if request.GET.get('l') == 'icons':
        context.update({'icons': 'OK'})
    
    context.update(csrf(request))
    return HttpResponse(template.render(context))

 
##
# Search for a product.
def search(request):
    if request.method == 'GET':
        form = SearchForm(request.GET)
       
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
                    'query'             : request.GET.get('query'),
                })

            # TODO: document me!
            else:
                context = RequestContext(request, {
                    'message'     : message,
                    'categories'  : categories,
                    'products'    : products,
                    'query'       : request.GET.get('query'),
                })
            
            
            if request.GET.get('l') == 'icons':
                context.update({'icons': 'OK'})
            context.update(csrf(request))
            return HttpResponse(template.render(context))
            
        else:
           return HttpResponseRedirect('/') 
           
    else:
        return HttpResponseRedirect('/')
