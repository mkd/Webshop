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
# Product form, either to add a new product or save an existing product.
class ProductForm(ModelForm):
    class Meta:
        model = Product
        widgets = {
            'picture'     : forms.ClearableFileInput,
            'description' : forms.Textarea,
        }
