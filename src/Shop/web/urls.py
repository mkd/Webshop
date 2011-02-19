from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^product/(?P<product_id>\d+)$', 'web.views.product'),
    (r'^product/(?P<product_id>\d+)/comment', 'web.views.comment'),  
    (r'^category/(?P<category_name>\w+)', 'web.views.category'),
    (r'^comment/(?P<comment_id>\d+)/(?P<option>(0|1))', 'web.views.rateComment'),
    (r'^search', 'web.views.search'), 
    (r'^cart/(?P<user_id>\d+)', 'web.views.cart'),
    #(r'^user/profile/(?P<user_id>)', 'web.views.profile'),
    (r'^index$', 'web.views.index'),
    (r'^$', 'web.views.index'),
    (r'^signup$', 'web.views.signup'),
    (r'^signin$', 'web.views.signin'),
    (r'^signout$', 'web.views.signout'),
    (r'^login$', 'web.views.login'),
    (r'^register$', 'web.views.register'),
    (r'^profile$', 'web.views.profile'),
    (r'^forgot_password', 'web.views.forgot_password'),
    (r'^save_profile', 'web.views.save_profile')
)
    
