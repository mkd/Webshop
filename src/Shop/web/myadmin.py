### myadmin.py
### This module contains the administrative functions of Webshop.
### (c) 2011 The Webshop Team

### necessary libraries ###
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import *
from django.template import Context, RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from utils import *
import os.path
from models import *
from forms import *
import datetime, hashlib, os


##
# Display the administration pages to staff personnel.
#
# Note: if the user is not staff, ask her to sign in with a staff account.
def myadmin(request):
    if is_staff(request):
        t = loader.get_template('myadmin.html')
        context = RequestContext(request, { })
        return HttpResponse(t.render(context))


##
# Render the products administration page.
#
# The products admin page renders a table with all the products, that can be
# sorted by name, price, popularity, etcetera.
def myadmin_products(request):
    if is_staff(request):
        # fetch the sorting criteria from GET
        column = request.GET.get('column', 'name')
        order  = request.GET.get('order', 'a')
        if order == 'a':
            criteria = column
        else:
            criteria = '-' + column

        # retrieve the products from the database
        products = Product.objects.all().order_by(criteria)
        if len(products) <= 0:
            products_no_0 = True
        else:
            products_no_0 = False
        t = loader.get_template('myadmin_products.html')
        context = RequestContext(request, {
            'products'      : products,
            'products_no'   : len(products),
            'products_no_0' : products_no_0,
            'column'        : column,
            'order'         : order,
        })
        return HttpResponse(t.render(context))


##
# Render a page to add a new product.
def myadmin_addProduct(request):
    if is_staff(request):
        form = ProductForm()
        t = loader.get_template('myadmin_add_product.html')
        context = RequestContext(request, {
            'form': form,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Add a product to the database.
def addProduct(request):
    if is_staff(request) and request.method == 'POST':
        # save all the data from the POST into the database
        p = Product.objects.create(
            name            = request.POST.get('name'),
            description     = request.POST.get('description', ''),
            category_id     = request.POST.get('category'),
            price           = request.POST.get('price', 0),
            stock_count     = request.POST.get('stock_count', 0),
            #tags           = request.POST['tags'],
        )
        p.save()

        # save icon
        handleUploadedPic('products', request.FILES.get('picture'), str(p.id))

        # load picture for the next view
        pic = 'web/static/images/products/' + str(p.id)
        if not os.path.exists(pic):
            pic = 'static/images/products/unknown.png'
        else:
            pic = 'static/images/products/' + str(p.id)

        # redirect the products management page
        t = loader.get_template('myadmin_edit_product.html')
        form = ProductForm(instance=p)
        context = RequestContext(request, {
            'product_name'  : p.name,
            'icon'          : pic,
            'product_added' : True,
            'form'          : form,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Render a page to edit a product.
def editProduct(request, product_id):
    if is_staff(request):
        t = loader.get_template('myadmin_edit_product.html')
        p = Product.objects.get(id=product_id)
        form = ProductForm(instance=p)

        # load the picture for the product
        pic = 'web/static/images/products/' + str(product_id)
        if not os.path.exists(pic):
            pic = 'static/images/products/unknown.png'
        else:
            pic = 'static/images/products/' + str(product_id)

        context = RequestContext(request, {
            'icon'         : pic,
            'form'         : form,
            'product_name' : p.name,
            'product_id'   : product_id,
        })
        return HttpResponse(t.render(context))


##
# Save a modified product.
def saveProduct(request, product_id):
    if is_staff(request) and request.method == 'POST':
        t = loader.get_template('myadmin_edit_product.html')

        # save all the data from the POST into the database
        p = Product.objects.get(id=product_id)
        p.name          = request.POST.get('name')
        p.description   = request.POST.get('description', '')
        p.category_id   = request.POST.get('category', 0)
        p.stock_count   = request.POST.get('stock_count', 0)
        p.price         = request.POST.get('price', 0)
        p.save()

        # save the icon, if available
        handleUploadedPic('products', request.FILES.get('picture'), str(p.id))

        # display editProduct again
        form = ProductForm(instance=p)

        # load the picture for the product
        pic = 'web/static/images/products/' + str(p.id)
        if not os.path.exists(pic):
            pic = 'static/images/products/unknown.png'
        else:
            pic = 'static/images/products/' + str(p.id)
        
        # redirect the user to the home page (already logged-in)
        form = ProductForm(instance=p)
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
# Render the categories administration page.
def myadmin_categories(request):
    if is_staff(request):
        return HttpResponseRedirect('/admin/web/category/')


# Render the orders administration page.
#
# The orders admin page renders a table with all the orders, that can be
# sorted by date, total sum, status, etcetera.
def myadmin_orders(request):
    if is_staff(request):
        # fetch the sorting criteria from GET
        column = request.GET.get('column', 'payment_date')
        order  = request.GET.get('order', 'a')
        if order == 'a':
            criteria = column
        else:
            criteria = '-' + column

        # retrieve the orders from the database
        orders = Payment.objects.all().order_by(criteria)
        if len(orders) <= 0:
            orders_no_0 = True
        else:
            orders_no_0 = False
        t = loader.get_template('myadmin_orders.html')
        context = RequestContext(request, {
            'orders'      : orders,
            'orders_no'   : len(orders),
            'orders_no_0' : orders_no_0,
            'column'      : column,
            'order'       : order,
        })
        return HttpResponse(t.render(context))


##
# Render the users administration page.
def myadmin_users(request):
    if is_staff(request):
        return HttpResponseRedirect('/admin/auth/user')


##
# Delete one product.
def deleteProduct(request, product_id):
    if is_staff(request):
        # delete product
        # note: comments are not necessarily deleted, because the user might want to
        # check a comment he or she wrote in the past (even if the product does not
        # exist anymore)
        t = loader.get_template('myadmin_products.html')

        product = Product.objects.get(pk=product_id)
        product.delete()

        # also delete the picture of the product
        if os.path.exists('web/static/images/products/' + str(product_id)):
            os.remove('web/static/images/products/' + str(product_id))

        # return to the products page
        products = Product.objects.all()
        context = RequestContext(request, {
            'products':  products,
            'deleted' :  True,
        })
        return HttpResponse(t.render(context))


##
# Delete a set of products.
def deleteProducts(request):
    if is_staff(request) and request.method == 'POST':
        # delete products
        # note: comments are not necessarily deleted, because the user might want to
        # check a comment he or she wrote in the past (even if the product does not
        # exist anymore)
        t = loader.get_template('myadmin_products.html')
        products = request.POST.getlist('product_list')
        # if no products to delete, then go back to products admin
        if len(products) <= 0:
            return HttpResponseRedirect('/myadmin_products')

        # if there are products to delete, go one by one
        # note: the picture of the product must be also deleted
        for p in products:
            product = Product.objects.get(pk=p)
            product.delete()
            # also delete the picture of the product
            if os.path.exists('web/static/images/products/' + str(p)):
                os.remove('web/static/images/products/' + str(p))

        # return to the products page
        products = Product.objects.all()
        context = RequestContext(request, {
            'products':  products,
        })
        return HttpResponse(t.render(context))


##
# Cancel a set of orders.
#
# Note: this view does not delete orders, just mark them as canceled.
def cancelOrders(request):
    if is_staff(request) and request.method == 'POST':
        # cancel orders
        t = loader.get_template('myadmin_orders.html')
        orders = request.POST.getlist('order_list')
        # if no products to delete, then go back to products admin
        if len(orders) <= 0:
            return HttpResponseRedirect('/myadmin_orders')

        # if there are products to delete, go one by one
        # note: the picture of the product must be also deleted
        for o in orders:
            od = Payment.objects.get(pk=o)
            od.status = 'Canceled'
            od.save()

        # return to the products page
        orders = Payment.objects.all()
        context = RequestContext(request, {
            'orders':  orders,
        })
        return HttpResponse(t.render(context))


##
# Cancel a given order.
#
# Note: this view does not delete orders, just mark them as canceled.
def cancelOrder(request, order_id):
    if is_staff(request):
        # cancel orders
        t = loader.get_template('myadmin_orders.html')
        o = Payment.objects.get(pk=order_id)
        o.status = 'Canceled'
        o.save()

        # return to the products page
        orders = Payment.objects.all()
        context = RequestContext(request, {
            'orders'   : orders,
            'order_id' : order_id,
            'canceled' : True,
        })
        return HttpResponse(t.render(context))


##
# Render a page to edit an order status.
def editOrder(request, order_id):
    if is_staff(request):
        t = loader.get_template('myadmin_edit_order.html')
        payment = Payment.objects.get(id=order_id)
        products = Transaction.objects.filter(payment=payment)
        form = OrderForm(instance=payment)

        context = RequestContext(request, {
            'form'       : form,
            'order'      : payment,
            'order_id'   : order_id,
            'products'   : products,
        })
        return HttpResponse(t.render(context))


##
# Save a modified product.
def saveOrder(request, order_id):
    if is_staff(request) and request.method == 'POST':
        t = loader.get_template('myadmin_edit_order.html')

        # save the status in the database
        o = Payment.objects.get(id=order_id)
        o.status = request.POST.get('status', 'Processing')
        o.save()

        # display editOrder again
        form = OrderForm(instance=o)

        # redirect the user to the home page (already logged-in)
        context = RequestContext(request, {
            'form'          : form,
            'order'         : o,
            'order_id'      : order_id,
            'order_saved'   : True,
        })

        # render response
        context.update(csrf(request))
        return HttpResponse(t.render(context))
