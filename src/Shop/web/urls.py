from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^product/(?P<product_id>\d+)', 'web.views.product'),    
    (r'^category/(?P<category_name>\w+)', 'web.views.category'), 
    #(r'^user/cart/(?P<user_id>)', 'web.views.cart'),
    #(r'^user/profile/(?P<user_id>)', 'web.views.profile'),
    (r'^index$', 'web.views.index'),
    (r'^$', 'web.views.index'),
    (r'^signup$', 'web.views.signup'),
)
    
