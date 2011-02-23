from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^product/(?P<product_id>\d+)/$', 'web.views.product'),
    (r'^editProduct/(?P<product_id>\d+)$', 'web.views.editProduct'),
    (r'^saveProduct/(?P<product_id>\d+)$', 'web.views.saveProduct'),
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
    (r'^checkout', 'web.views.checkout'),
    (r'^success', 'web.views.paymentOk'),
    (r'^cancel', 'web.views.paymentNo'),
    (r'^error', 'web.views.paymentError'),
    
    (r'^signup$', 'web.views.signup'),
    (r'^signin$', 'web.views.signin'),
    (r'^signout$', 'web.views.signout'),
    (r'^login$', 'web.views.tryLogin'),
    (r'^register$', 'web.views.register'),
    (r'^editProfile$', 'web.views.editProfile'),
    (r'^forgot_password$', 'web.views.forgot_password'),
    (r'^saveProfile$', 'web.views.saveProfile'),
    
    (r'^myadmin$', 'web.views.myadmin'),
    (r'^myadmin_page$', 'web.views.myadmin_page'),
    (r'^myadmin_products$', 'web.views.myadmin_products'),
    (r'^myadmin_categories$', 'web.views.myadmin_categories'),
    (r'^myadmin_orders$', 'web.views.myadmin_orders'),

    (r'^deleteOrders$', 'web.views.deleteOrders'),
    (r'^myadmin_addProduct$', 'web.views.myadmin_addProduct'),

    (r'^deleteProducts', 'web.views.deleteProducts'),  
    (r'^addProduct', 'web.views.addProduct'),

    (r'^$', 'web.views.index'),
)
