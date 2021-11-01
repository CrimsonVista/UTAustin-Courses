from django import forms
from django.contrib.auth.models import User
from .models import NewsListing

class UpdateUserForm(forms.Form):
    update_user_select = forms.ModelChoiceField(
        label="Username",
        queryset=User.objects.filter(is_superuser=False))
    update_user_token    = forms.CharField(label="Token ID", required=False)
    update_user_secrecy  = forms.IntegerField(label="Secrecy Level")
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
        
class CreateNewsForm(forms.Form):
    new_news_query = forms.CharField(label="New Query", required=False)
    new_news_sources = forms.CharField(label="Sources", required=False)
    new_news_secrecy = forms.IntegerField(label="Secrecy Level", required=False)
    
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.user_secrecy = 0
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
        
class UpdateNewsForm(forms.Form):
    update_news_select = forms.ModelChoiceField(
        label="Update News",
        queryset=NewsListing.objects.all(),
        required=False)
    update_news_query   = forms.CharField(label="Update Query", required=False)
    update_news_sources = forms.CharField(label="Update Sources", required=False)
    update_news_secrecy = forms.IntegerField(label="Update Secrecy", required=False)
    
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data