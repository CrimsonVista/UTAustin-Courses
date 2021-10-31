"""newsapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django import forms
from newslister.models import UserXtraAuth
from newslister.views import register_view, account, oauth_view, oauth_callback_view

class TokenLoginForm(AuthenticationForm):
    def clean(self):
        # STUDENT TODO:
        # This is where password processing takes place.
        # For 2-factor authentication, you need to
        # check that the token number is appended to
        # the end of the password entered by the user
        # You don't need to check the password; Django is
        # doing that.
        if not UserXtraAuth.objects.filter(username=self.cleaned_data['username']).exists():
            # User not found. Set secrecy to 0
            user_secrecy = 0
        else:
            user_xtra_auth = UserXtraAuth.objects.get(username=self.cleaned_data['username'])
            user_secrecy = user_xtra_auth.secrecy
            
        # the password in the form in self._cleaned_data['password']
        # Edit self.cleaned_data['password'] based on the user secrecy level
        return super().clean()

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name="registration/login.html",
        authentication_form=TokenLoginForm), 
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(
        template_name="registration/logout.html"),
        name='logout'
    ),
    path('register/', register_view,
        name="register"),
    path('admin/', admin.site.urls),
    # This line will look for urls in app
    path('',include('newslister.urls')),
    path('newslist/',include('newslister.urls')),
    path('account/',account, name="account"),
    path('oauth/callback', oauth_callback_view, name='oauth_callback'),
    path('oauth/', oauth_view, name='oauth'),
]
