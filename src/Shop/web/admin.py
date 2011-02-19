from django.contrib import admin
from models import Product, Category, Tag, Comment, Transaction, CartProduct

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Transaction)
admin.site.register(CartProduct)
