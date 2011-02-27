### models.py
### This module contains the database definitions for each component that is
### used in the Webshop project.
### (c) 2011 The Webshop Team



### necessary libraries ###
from django.db import models
from django.utils.datetime_safe import datetime
from django.template.defaultfilters import default
from django.contrib.admin.models import User
from django.db.models.signals import post_save
import math, md5



##
# Model: UserProfile
# 
# Uses the built in django.contrib.auth to manage users and athentication.
# Adds fields to manage the postal information of the user.
#
# user             references the built in user class of django.
# picture          path to the static file containing the user profile's picture
# postal_address   The street, number and flat to deliver the product.
# postal_code      The zip or postal code.
# postal_city      The city.
# postal_country   The country.
class UserProfile( models.Model ):
    user           = models.ForeignKey( User, unique=True)
    products_in_cart = models.IntegerField( default=0 )
    picture        = models.CharField(  max_length=256 )
    postal_address = models.CharField(  max_length=160 )
    postal_code    = models.CharField(  max_length=5 )
    postal_city    = models.CharField(  max_length=20 )
    postal_country = models.CharField(  max_length=20 )
    
    def get_user(self):
        return self.__user

    def set_user(self, value):
        self.__user = value
   
    def __unicode__(self):
        return self.user.name

##
# Activates the create_user_profile handler when a new user is saved.
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


##
# Model: Category
#
# This model represents a category where products can be included. Typically,
# products should belong only to one category. However, they may belong to
# several tags.
#
# @see Product
# @see Tag
#
# id          implicit ID field (automatically generated)
# name        name of the category
# description text describing the category
# icon        string with the path to the icon associated to the category
# parent_id   ID of the parent category, if any (i.e. subcategory)
class Category(models.Model):
    name        = models.CharField( max_length=32, blank = False )
    description = models.CharField( max_length=256, blank=True )
    icon        = models.CharField( max_length=256, default = 'images/categories/unknown.png' )
    parent_id   = models.ForeignKey('self', related_name='parent', null=True, blank=True, default=-1)
    
    def __unicode__(self):
        return self.name
    

##
# Model: Tag
#
# This model represents a tag to which products can be associated. A product may
# have as many tags as desired. Tags are created on the fly, as necessary.
# Please do not confuse tags with categories.
#
# @see Product
# @see Tag
#
# id          implicit ID field (automatically generated)
# name        name of the tag
class Tag(models.Model):
    name        = models.CharField( max_length=16, blank=False )

    def __unicode__(self):
        return self.name
    
 
##
# Model: Product
#
# This model represents the main object which can be bought, commented, voted, and added by users
#
# @see: Category
# @see: Tag
#
# tag_id          id of the tag which the product belongs to. A product can belong to multiple tags and a tag can be for many products
# category_id     id of the category which the products belongs to. A product can only belong to one category.
# name            the name of the product
# description     additional description of the product
# price           a decimal field containing the price of the product (e.g. 99.50)
# stock_count     the number of products in stock. Descending field. (can also be a query. no need to keep in db)
# sold_count      the number of sold products until now. Incremental field (can also be a query. no need to keep in db)
# comment_count   the number of comments made for the product. Incremental field. (can also be a query. no need to keep in db)
# visit_count     Incremental field. Incremented per user view of the product
# average rating  gets the average rating of all users for the product (a jt table is necessary to get user-table relation)

class Product(models.Model):
    tags            = models.ManyToManyField( Tag, blank=True)
    category        = models.ForeignKey(Category)
    name            = models.CharField( max_length=32 )
    short_name      = models.CharField( max_length=14, default = '' )
    description     = models.CharField( max_length=512, default = '' )   
    picture         = models.CharField( max_length=256, default = '/static/images/products/unknown.png' )
    price           = models.FloatField( default=1 )
    stock_count     = models.IntegerField( default=0 )
    sold_count      = models.IntegerField( default=0 )
    comment_count   = models.IntegerField( default=0 )
    visit_count     = models.IntegerField( default=0 )
    average_rating  = models.IntegerField( default=0 ) 
    votes           = models.IntegerField( default=0 )
    points          = models.IntegerField( default=0 )
    
    def save(self, *args, **kwargs):
        if self.votes > 0:
            self.average_rating = self.points / self.votes
            
        if self.short_name[:10] != self.name[:10]:
            if len(self.name) > 10:
                self.short_name = self.name[:10] + '...'
            else: 
                self.short_name = self.name    
                
        super(Product, self).save(*args, **kwargs)
        return self
      
    def __unicode__(self):
        return self.name


##
# Model: CartProduct
#
# This model represents one product information inside a shopping card. There could be multiple products inside a cart and there can be multiple counts of a certain product
# 
# @see: Cart
# @see: Product
# 
# product_id      id of the product inside a cart
# cart_id         id of the cart that the product belongs to
# timestamp       date information of when the product was added to the cart
# quantity        quantity of a the product inside the cart
# 
class CartProduct(models.Model):
    product     = models.ForeignKey(Product)
    user        = models.ForeignKey(User)
    timestamp   = models.DateTimeField( default=datetime.now)
    quantity    = models.IntegerField( default=0 )
    total       = 0
    
    def save(self, force_insert=False, force_update=False):
        self.user.get_profile().products_in_cart += self.quantity
        super(CartProduct, self).save()
        return self
        
    def __unicode__(self):
        return self.product + " by " + self.user


##
# Model: Payment
#
# Implement the equivalent to order, containing an user, a total amount and a
# status for the delivery.
class Payment(models.Model):
    pid            = models.CharField( max_length=500 )
    user           = models.ForeignKey(User)
    checksum       = models.CharField( max_length=300 )
    ref            = models.IntegerField( default=-1 )
    amount         = models.IntegerField( default=0 )   
    payment_date   = models.DateTimeField( default=datetime.now )
    status         = models.CharField( max_length=100, default='Processing' )
    postal_address = models.CharField( max_length=160 )
    postal_code    = models.CharField( max_length=5 )
    postal_city    = models.CharField( max_length=20 )
    postal_country = models.CharField( max_length=20 )


##
# Model: Transaction
#
# product          The item sold.
# user             Who buy the item.
# payment_date     When the user pays for the products.
# quantity         The number of products that the user bought.
# unit_price       The price that the user pays for the product, only for 1.
# rate             Once the user buy the product he can rate it.
# postal_address   The street, number and flat to deliver the product.
# postal_code      The zip or postal code.
# postal_city      The city.
# postal_country   The country.
class Transaction( models.Model ):
    user           = models.ForeignKey(User)
    product        = models.ForeignKey( Product )
    payment        = models.ForeignKey( Payment )
    quantity       = models.IntegerField( default=1 )
    unit_price     = models.FloatField( default=0)
    total          = models.IntegerField( default=0 )
    rate           = models.IntegerField( default=0 )
    
    def save(self, force_insert=False, force_update=False):
        self.total = self.unit_price * self.quantity
        super(Transaction, self).save()
        return self
    
    def __unicode__(self):
        return "%s: %s (%d)" % (self.user.username, self.product.name, self.quantity)


##
# Model: Comment
#
# This model represents a comment from a user.
#
# id         implicit ID field (automatically generated)
# product_id ID of the product to which the comment is attached
# user_id    ID of the user who wrote the comment
# timestamp  date and time when the comment was written
# parent_id  ID of the parent to this comment, if any (i.e. reply)
# positives  number of positive votes to this comment
# negatives  number of negative votes to this comment
#
# Positives and negatives are votes for comments. This is an extra feature that
# can give reliability to certain users, depending on their comments. There
# might be useless comments and useful comments, and hence users should be able
# to also rate comments.

class Comment(models.Model):
    product = models.ForeignKey(Product)
    user    = models.ForeignKey(User)
    timestamp  = models.DateTimeField( default=datetime.now, blank=False )
    comment    = models.CharField( max_length=300 )
    parent_id  = models.ForeignKey('self', related_name='parent', null=True, blank=True)
    positives  = models.PositiveIntegerField( default = 0 )
    negatives  = models.PositiveIntegerField( default = 0 )
    hasProduct = models.BooleanField( default = False)

    def __unicode__(self):
        return self.user.username + " en " + self.product.name
    
    def save(self, force_insert=False, force_update=False):
        try:
            transaction = Transaction.objects.filter(product=self.product, user=self.user)
            if transaction:
                self.hasProduct = True
            else:
                self.hasProduct = False
            
        except Transaction.DoesNotExist: 
            self.hasProduct = False
            
        super(Comment, self).save()
        return self

    
##
# Model: ItemStats
#
# This model represents the product statistic for a given time. For instance daily/hourly product statistics
#
# @see: Product
#
# product_id      id of the product
# date            date of the statistics (should this be time period?)
# visit_count     visit count for the product in the given time 
# sold_count      number of sold products in the given time
# comment_count   number of user comments for the product in the given time
class ItemStats(models.Model):
    product_id      = models.ForeignKey(Product)
    date            = models.DateTimeField( default=datetime.now)
    visit_count     = models.IntegerField( default=0 )
    sold_count      = models.IntegerField( default=0 )
    comment_count   = models.IntegerField( default=0 )


##
# Model: Shop stats
# 
# Stores daily info of the webshop
# In order to avoid several operation each time that statistical are render, at the end of the day 
# the application saves all the information.
#
# date                 Day of the stats.
# number_new_users     Number of new registered users this day.
# number_sold_products Number of products sold this day.
# number_new_comments  Number of comments wrote this day.
# number_new_products  Number of new products added to the shop this day.
class ShopStats():
    date = models.DateTimeField( default=datetime.now(), unique=True )
    number_visits        = models.IntegerField( default=0 )
    number_new_users     = models.IntegerField( default=0 )
    number_sold_products = models.IntegerField( default=0 )
    number_new_comments  = models.IntegerField( default=0 )
    number_new_products  = models.IntegerField( default=0 ) 
