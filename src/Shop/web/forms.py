from django import forms
from django.forms import widgets

class CommentForm(forms.Form): 
    comment = forms.CharField(label=u'Your comment', max_length=300, widget=forms.Textarea) 
    
class SearchForm(forms.Form):
    query = forms.CharField( max_length=60, widget=forms.Textarea ) 

class RegisterForm(forms.Form):
    picture         = forms.FileField( )
    fname           = forms.CharField( max_length=16 )
    sname           = forms.CharField( max_length=16 )
    user            = forms.CharField( max_length=16 )
    passwd          = forms.CharField( widget=forms.PasswordInput() )
    pass2           = forms.CharField( widget=forms.PasswordInput() )
    email           = forms.CharField( max_length=32 )
    email2          = forms.CharField( max_length=32 )

class ProfileForm(forms.Form):
    picture         = forms.FileField( )
    fname           = forms.CharField( max_length=16 )
    sname           = forms.CharField( max_length=16 )
    user            = forms.CharField( max_length=16 )
    passwd          = forms.CharField( widget=forms.PasswordInput() )
    pass2           = forms.CharField( widget=forms.PasswordInput() )
    email           = forms.CharField( max_length=32 )
    email2          = forms.CharField( max_length=32 )
    postal_address  = forms.CharField( widget=forms.TextInput() )
    postal_code     = forms.CharField( max_length=5 )
    postal_city     = forms.CharField( )
    postal_country  = forms.CharField( )
