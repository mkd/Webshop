from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^product/(?P<product_id>\d+)$', 'web.views.product'),
    (r'^edit_product/(?P<product_id>\d+)$', 'web.views.edit_product'),
    (r'^product/(?P<product_id>\d+)/comment', 'web.views.comment'),  
    (r'^category/(?P<category_name>\w+)', 'web.views.category'),
    (r'^edit_category/(?P<category_name>\w+)', 'web.views.edit_category'),
    (r'^edit_user/(?P<user_id>\w+)', 'web.views.edit_user'),
    (r'^edit_order/(?P<order_id>\w+)', 'web.views.edit_order'),
    (r'^comment/(?P<comment_id>\d+)/(?P<option>(0|1))', 'web.views.rateComment'),
    (r'^search', 'web.views.search'), 
    (r'^cart$', 'web.views.cart'),
    (r'^index$', 'web.views.index'),
    (r'^$', 'web.views.index'),
    (r'^signup$', 'web.views.signup'),
    (r'^signin$', 'web.views.signin'),
    (r'^signout$', 'web.views.signout'),
    (r'^login$', 'web.views.try_login'),
    (r'^register$', 'web.views.register'),
    (r'^profile$', 'web.views.profile'),
    (r'^forgot_password$', 'web.views.forgot_password'),
    (r'^save_profile$', 'web.views.save_profile'),
    (r'^myadmin$', 'web.views.myadmin'),
    (r'^myadmin_page$', 'web.views.myadmin_page'),
    (r'^myadmin_products$', 'web.views.myadmin_products'),
    (r'^myadmin_categories$', 'web.views.myadmin_categories'),
    (r'^myadmin_users$', 'web.views.myadmin_users'),
    (r'^myadmin_orders$', 'web.views.myadmin_orders'),
    (r'^myadmin_add_product', 'web.views.myadmin_add_product'),
    (r'^categoryNew$', 'web.views.render_new_category'),
    (r'^categoryList$', 'web.views.render_list_category'),
    (r'^categoryInsert$', 'web.views.insert_category'),
    (r'^categoryDelete', 'web.views.delete_selected_categories'),  
    (r'^add_product', 'web.views.add_product'),
)
