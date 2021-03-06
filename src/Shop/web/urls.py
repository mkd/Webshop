### urls.py
### Regular expressions to guide the user through the Webshop navigation.
### (c) 2011 The Webshop Team


### necessary libraries ###
from django.conf.urls.defaults import *



### URL patterns definitions ###
urlpatterns = patterns('',
    (r'^product/(?P<product_id>\d+)/$', 'web.views.product'),
    (r'^product/(?P<product_id>\d+)/comment/$', 'web.views.comment'),
    (r'^category/(?P<category_id>\d+)/$', 'web.views.category'),
    (r'^comment/(?P<comment_id>\d+)/(?P<option>(0|1))$', 'web.views.rateComment'),
    (r'^search$', 'web.views.search'), 
    
    (r'^cart$', 'web.views.cart'),
    (r'^cart/add$', 'web.views.addToCart'),
    (r'^cart/del$', 'web.views.deleteFromCart'),
    (r'^cart/edit$', 'web.views.editQuantityInCart'),
    
    (r'^myProducts/(?P<payment_id>\d+)$', 'web.views.myProducts'),
    (r'^myProducts/product/rate$', 'web.views.rateProduct'),
    (r'^myTransactions$', 'web.views.myTransactions'),
    (r'^checkout$', 'web.views.checkout'),
    (r'^checkout/set/postal$', 'web.views.updatePostalOrder'),
    (r'^success$', 'web.views.paymentOk'),
    (r'^cancel$', 'web.views.paymentNo'),
    (r'^error$', 'web.views.paymentError'),
    
    (r'^signup/$', 'web.views.signup'),
    (r'^signin/$', 'web.views.signin'),
    (r'^signout/$', 'web.views.signout'),
    (r'^editProfile$', 'web.views.editProfile'),
    (r'^forgot_password$', 'web.views.forgot_password'),
    (r'^saveProfile$', 'web.views.saveProfile'),
    
    (r'^myadmin$', 'web.views.myadmin'),
    (r'^myadmin_products$', 'web.views.myadmin_products'),
    (r'^myadmin_categories$', 'web.views.myadmin_categories'),
    (r'^myadmin_orders$', 'web.views.myadmin_orders'),
    (r'^myadmin_addProduct$', 'web.views.myadmin_addProduct'),
    (r'^editProduct/(?P<product_id>\d+)$', 'web.views.editProduct'),
    (r'^addProduct$', 'web.views.addProduct'),
    (r'^saveProduct/(?P<product_id>\d+)$', 'web.views.saveProduct'),
    (r'^deleteProducts$', 'web.views.deleteProducts'),  
    (r'^deleteProduct/(?P<product_id>\d+)$', 'web.views.deleteProduct'),
    (r'^cancelOrders$', 'web.views.cancelOrders'),
    (r'^editOrder/(?P<order_id>\d+)$', 'web.views.editOrder'),
    (r'^cancelOrder/(?P<order_id>\d+)$', 'web.views.cancelOrder'),
    (r'^saveOrder/(?P<order_id>\d+)$', 'web.views.saveOrder'),
    (r'^sendPassword$', 'web.views.sendPassword'),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static'}),

    (r'^$', 'web.views.index'),
)
