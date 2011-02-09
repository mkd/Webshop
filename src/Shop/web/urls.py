from django.conf.urls.defaults import *

urlpatterns = patterns('',
<<<<<<< HEAD
    (r'^product/(?P<product_id>)', 'web.views.product'),    
    #(r'^category/(?P<category_id>)', 'web.views.category'), 
    #(r'^user/cart/(?P<user_id>)', 'web.views.cart'),
    #(r'^user/profile/(?P<user_id>)', 'web.views.profile'),
    (r'^index$', 'web.views.index'),
    (r'^$', 'web.views.index'),
    (r'^signup$', 'web.views.signup'),
)
=======
    (r'$product/(?P<product_id>)', 'web.views.product'),    
    (r'$category/(?P<category_id>)', 'web.views.category'), 
    (r'$user/cart/(?P<user_id>)', 'web.views.cart'),
    (r'$user/profile/(?P<user_id>)', 'web.views.profile'),
    (r'index$', 'web.views.index'),
    (r'$', 'web.views.index'),
>>>>>>> parent of 70feabc... Updated urls.py.
    
)
    
