### necessary Django modules ###
from django import forms
from django.forms import widgets
from models import *



### custom functionality ###
##
# Retrieve a list of categories and create a list ready to be used as a dropdown
# list.
def all_categories():
    cats = Category.objects.all()
    categories = [('', '')]
    for c in cats:
        categories.append((c.id, c.name))
    return categories


### custom forms ###
##
# Form to leave a comment.
class CommentForm(forms.Form): 
    comment = forms.CharField(label=u'Your comment', max_length=300, widget=forms.Textarea) 
    

##
# Form to perform a quick search.
class SearchForm(forms.Form):
    query = forms.CharField( max_length=60, widget=forms.Textarea ) 


##
# Form to ask the user for the website's master password.
class AdminForm(forms.Form):
    query = forms.CharField( widget=forms.PasswordInput ) 


##
# Form for user registration.
class RegisterForm(forms.Form):
    picture         = forms.FileField( )
    fname           = forms.CharField( max_length=16 )
    sname           = forms.CharField( max_length=16 )
    user            = forms.CharField( max_length=16 )
    passwd          = forms.CharField( widget=forms.PasswordInput )
    pass2           = forms.CharField( widget=forms.PasswordInput )
    email           = forms.CharField( max_length=32 )
    email2          = forms.CharField( max_length=32 )


##
# Form for user profile.
class ProfileForm(forms.Form):
    picture         = forms.FileField( )
    fname           = forms.CharField( max_length=16 )
    sname           = forms.CharField( max_length=16 )
    user            = forms.CharField( max_length=16 )
    passwd          = forms.CharField( widget=forms.PasswordInput )
    pass2           = forms.CharField( widget=forms.PasswordInput )
    email           = forms.CharField( max_length=32 )
    email2          = forms.CharField( max_length=32 )
    postal_address  = forms.CharField(  )
    postal_code     = forms.CharField( max_length=5 )
    postal_city     = forms.CharField( )
    postal_country  = forms.CharField( )


##
# Form to add a new product.
class AddProductForm(forms.Form):
    picture         = forms.FileField()
    name            = forms.CharField( max_length=20 )
    desc            = forms.CharField( max_length=500, widget=forms.Textarea )
    price           = forms.IntegerField( min_value=1 )
    units           = forms.IntegerField( min_value=0 )
    #tags            = forms.CharField( max_length=64 )
    category        = forms.ChoiceField( choices=all_categories() )


##
# Form to edit a product.
class EditProductForm(forms.Form):
    picture         = forms.FileField()
    name            = forms.CharField( max_length=20 )
    desc            = forms.CharField( max_length=500, widget=forms.Textarea )
    price           = forms.IntegerField( min_value=1 )
    units           = forms.IntegerField( min_value=0 )
    #tags            = forms.CharField( max_length=64 )
    category        = forms.ChoiceField( choices=all_categories() )


##
# Form to add a new category.
class AddCategoryForm(forms.Form):
    picture         = forms.FileField()
    name            = forms.CharField( max_length=20 )
    desc            = forms.CharField( max_length=500, widget=forms.Textarea )
    parent          = forms.ChoiceField( choices=all_categories() )
 
 
##
# Form to add a new category.  
class NewCategoryForm(forms.Form):
    name = forms.CharField(label=u'Category Name', max_length=20, widget=forms.TextInput) 
    description = forms.CharField(label=u'Category Description', max_length=100, widget=forms.Textarea)
    icon = forms.CharField(label=u'Directory', widget=forms.TextInput)
