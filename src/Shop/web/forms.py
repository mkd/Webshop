from django import forms
from django.forms import widgets

class CommentForm(forms.Form): 
    comment = forms.CharField(label=u'Your comment', max_length=300, widget=forms.Textarea) 
    
class SearchForm(forms.Form):
    query = forms.CharField( max_length=60, widget=forms.Textarea ) 