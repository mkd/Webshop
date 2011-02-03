### models.py
from django.db import models


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
    timestamp  = models.DateTimeField()
    parent_id  = models.ForeignKey(Comment)
    positives  = models.PositiveIntegerField()
    negatives  = models.NegativeIntegerField()


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
    name        = models.CharField()
    description = models.CharField()
    icon        = models.CharField()
    parent_id   = models.ForeignKey(Category) 


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
    name        = models.CharField()
