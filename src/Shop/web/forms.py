from django import forms
from django.forms import widgets

class CommentForm(forms.Form): 
    comment = forms.CharField(label=u'Your comment', max_length=300, widget=forms.Textarea) 
    