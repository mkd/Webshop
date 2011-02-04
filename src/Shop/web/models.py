## necessary libraries
from django.db import models
from django.utils.datetime_safe import datetime
from django.template.defaultfilters import default
from django.contrib.admin.models import User
from django.db.models.signals import post_save


##
# Model: User
# 
# Uses the built in django.contrib.auth to manage users and athentication.
# Adds fields to manage the postal information of the user.
#
# user             references the built in user class of django.
# postal_address   The street, number and flat to deliver the product.
# postal_code      The zip or postal code.
# postal_city      The city.
# postal_country   The country.
class UserProfile( models.Model ):
    user           = models.ForeignKey( User, unique=True )
    postal_address = models.CharField( max_length=160 )
    postal_code    = models.CharField( max_length=5 )
    postal_city    = models.CharField( max_length=20 )
    postal_country = models.CharField( max_length=20 )
    
    def __unicode__(self):
        return self.user.name

##
# Activates the create_user_profile handler when a new user is saved.
User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


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
    product        = models.ForeignKey( Product )
    user           = models.ForeignKey( User )
    payment_date   = models.DateTimeField( default=datetime.now )
    quantity       = models.IntegerField( default=1 )
    unit_price     = models.FloatField( default=product_id.price) 
    rate           = models.IntegerField()
    postal_address = models.CharField( max_length=160 )
    postal_code    = models.CharField( max_length=5 )
    postal_city    = models.CharField( max_length=20 )
    postal_country = models.CharField( max_length=20 )
    
    def __unicode__(self):
        return self.user.name + ": " + self.product.name + "(" + self.quantity + ")"


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
    product_id = models.ForeignKey(Product)
    user_id    = models.ForeignKey(User)
    timestamp  = models.DateTimeField( default=datetime.now, blank=False )
    parent_id  = models.ForeignKey(Comment, default = -1)
    positives  = models.PositiveIntegerField( default = 0 )
    negatives  = models.NegativeIntegerField( default = 0 )

    # accessors
    def getProduct(self):
        return self.product_id

    def setProduct(self, p):
        self.product_id = p

    def getUser(self):
        return self.user_id

    def setUser(self, u):
        self.user_id = u

    def getDate(self):
        return self.timestamp

    def setDate(self, d):
        self.timestamp = d

    def getParent(self):
        return self.parent_id

    def setParent(self, pid):
        self.parent_id = pid

    def getPos(self):
        return self.positives

    def setPos(self, p):
        self.positives = p

    def incPos(self):
        self.positives += 1

    def decPos(self):
        self.positives -= 1

    def getNeg(self):
        return self.negatives

    def setNeg(self, n):
        self.negatives = n

    def incNeg(self):
        self.negatives += 1

    def decNeg(self):
        self.negatives -= 1


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
    name        = models.CharField( blank = False )
    description = models.CharField( default = '' )
    icon        = models.CharField( deafult = 'images/categories/unknown.png' )
    parent_id   = models.ForeignKey(Category, default = -1) 

    # accessors
    def getName(self):
        return self.name

    def setName(self, n):
        self.name = n

    def getDesc(self):
        return self.description

    def setDesc(self, d):
        self.description = d

    def getIconPath(self):
        return self.icon

    def setIconPath(self, ip):
        self.icon = ip

    def getParent(self):
        return self.parent_id

    def setParent(self, pid):
        self.parent_id = pid


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
    name        = models.CharField( blank=False )

    # accessors
    def getName(self):
        return self.name

    def setName(self, n):
        self.name = n
