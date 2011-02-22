from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^product/(?P<product_id>\d+)', 'web.views.product'),
    (r'^editProduct/(?P<product_id>\d+)', 'web.views.editProduct'),
    (r'^product/(?P<product_id>\d+)/comment', 'web.views.comment'),
    (r'^category/(?P<category_id>\d+)', 'web.views.category'),
    (r'^editCategory/(?P<category_name>\w+)', 'web.views.editCategory'),
    (r'^editUser/(?P<user_id>\w+)', 'web.views.edit_user'),
    (r'^comment/(?P<comment_id>\d+)/(?P<option>(0|1))', 'web.views.rateComment'),
    (r'^search', 'web.views.search'), 
    
    (r'^cart$', 'web.views.cart'),
    (r'^cart/add$', 'web.views.addToCart'),
    (r'^cart/del$', 'web.views.deleteFromCart'),
    (r'^cart/edit$', 'web.views.editQuantityInCart'),
    
    (r'^myProducts/(?P<payment_id>\d+)$', 'web.views.myProducts'),
    (r'^myProducts/product/rate', 'web.views.rateProduct'),
    (r'^myTransactions$', 'web.views.myTransactions'),
    (r'^checkout$', 'web.views.checkout'),
    (r'^success', 'web.views.paymentOk'),
    (r'^cancel', 'web.views.paymentNo'),
    
    (r'^signup$', 'web.views.signup'),
    (r'^signin$', 'web.views.signin'),
    (r'^signout$', 'web.views.signout'),
    (r'^login$', 'web.views.tryLogin'),
    (r'^register$', 'web.views.register'),
    (r'^profile$', 'web.views.profile'),
    (r'^forgot_password$', 'web.views.forgot_password'),
    (r'^saveProfile$', 'web.views.saveProfile'),
    
    (r'^myadmin$', 'web.views.myadmin'),
    (r'^myadmin_page$', 'web.views.myadmin_page'),
    (r'^myadmin_products$', 'web.views.myadmin_products'),
    (r'^myadmin_categories$', 'web.views.myadmin_categories'),
    (r'^myadmin_users$', 'web.views.myadmin_users'),
    (r'^myadmin_orders$', 'web.views.myadmin_orders'),

    (r'^myadmin_deleteOrders$', 'web.views.myadmin_delete_orders'),
    (r'^myadmin_addProduct', 'web.views.myadmin_addProduct'),
    (r'^myadmin_addCategory', 'web.views.myadmin_add_category'),

    (r'^categoryNew$', 'web.views.render_newCategory'),
    (r'^categoryList$', 'web.views.render_listCategory'),
    (r'^categoryInsert$', 'web.views.insert_category'),
    (r'^deleteCategories', 'web.views.deleteCategories'),  

    (r'^deleteProducts', 'web.views.deleteProducts'),  
    (r'^addProduct', 'web.views.addProduct'),
    (r'^addCategory', 'web.views.addCategory'),

    (r'^$', 'web.views.index'),
)
