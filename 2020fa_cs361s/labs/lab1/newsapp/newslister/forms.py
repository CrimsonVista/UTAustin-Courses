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
        # STUDENT TODO
        # This is where the "update user" form is validated.
        # The "cleaned_data" is a dictionary with the data
        # entered from the POST request. So, for example,
        # cleaned_data["update_user_secrecy"] returns that
        # form value. You need to update this method to
        # enforce the security policies related to tokens
        # and secrecy.
        # Return a "ValidationError(<err msg>)" if something 
        # is wrong
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
        # STUDENT TODO
        # This is where newslisting update form is validated.
        # The "cleaned_data" is a dictionary with the data
        # entered from the POST request. So, for example,
        # cleaned_data["new_news_query"] returns that
        # form value. You need to update this method to
        # enforce the security policies related to tokens
        # and secrecy.
        # Return a "ValidationError(<err msg>)" if something 
        # is wrong
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
    
    def clean(self):
        cleaned_data = super().clean()
        # STUDENT TODO
        # This is where newslisting update form is validated.
        # The "cleaned_data" is a dictionary with the data
        # entered from the POST request. So, for example,
        # cleaned_data["new_news_query"] returns that
        # form value. You need to update this method to
        # enforce the security policies related to tokens
        # and secrecy.
        # Return a "ValidationError(<err msg>)" if something 
        # is wrong
        return cleaned_data