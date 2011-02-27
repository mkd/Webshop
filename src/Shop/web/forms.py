### forms.py
### This module contains all the form definitions for Webshop.
### (c) 2011 The Webshop Team.



### necessary Django modules ###
from django import forms
from django.forms import widgets, ModelForm, ClearableFileInput
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
    comment = forms.CharField(
        label       = u'Leave a comment',
        max_length  = 300,
        widget      = forms.Textarea(attrs={
            'rows': '2',
            'cols': '64',
            'style' : 'vertical-align: top',
        })) 
    

##
# Form to perform a quick search.
class SearchForm(forms.Form):
    query = forms.CharField( max_length=60, widget=forms.Textarea ) 


##
# Passowrd recovery form.
class PassForm(forms.Form):
    email = forms.EmailField(
        label       = u'Your email address:',
        max_length  = 32,
    ) 


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
# Form for postal information of a payment.
class PostalForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('postal_address', 'postal_code', 'postal_city', 'postal_country')


##
# Product form, either to add a new product or save an existing product.
class ProductForm(ModelForm):
    class Meta:
        model = Product
        widgets = {
            'picture'     : forms.ClearableFileInput,
            'description' : forms.Textarea,
        }


##
# Order form, just used for editing an order status.
class OrderForm(ModelForm):
    class Meta:
        model = Payment
