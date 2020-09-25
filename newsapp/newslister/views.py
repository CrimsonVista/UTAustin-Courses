from django.shortcuts import render

# Create your views here.

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import NewsListing, UserXtraAuth
from .forms import UpdateUserForm, CreateNewsForm, UpdateNewsForm
import importlib.util
#from newsapi import NewsApiClient, newsapi_exception
import json, random, string, urllib

key_char_set = string.ascii_letters + string.digits

def random_key(keylen):
    return "".join([random.choice(key_char_set) for i in range(keylen)])

class NewsApiManager:
    def __init__(self):
        self.secrecy = 0
        # Initializing API KEY
        #self.newsapi = NewsApiClient(api_key='ae1a7d73cea847f0ada3fa537ab6f46d')
        self.errors = []
        self.data = []
        #self.update_articles()

    def update_articles(self):
        all_queries = NewsListing.objects.all()
        all_results = []
        self.errors = []
        for q in all_queries:
            # STUDENT TODO:test_form_
            # Currently, all queries are returned with out
            # respect to secrecy level. You need to implement
            # the "Simple Security Property" and the "* Property"
            # (of the Bell Lapadula model).
            #
            # the current secrecy of the viewer is in "self.secrecy"
            # the secrecy level of the query is in "q.secrecy"
            if q.secrecy <= self.secrecy:
                escaped_query = urllib.parse.quote(q.query)
                escaped_sources = '"{}"'.format(urllib.parse.quote(q.sources.replace('"',"")))
                all_results.append((q, escaped_query, escaped_sources))

        self.data = all_results

    def update_secrecy(self, secrecy):
        if secrecy == self.secrecy and self.data: return
        self.secrecy = secrecy
        self.update_articles()

newsmanager = NewsApiManager()

def index(request):
    # This processes the main index view.
    # If the user is authenticated, use their secrecy level
    # otherwise, secrecy level is 0.
    user_secrecy = 0
    if request.user.is_authenticated and not request.user.is_superuser and UserXtraAuth.objects.filter(username=request.user.username).exists():
        user_xtra_auth = UserXtraAuth.objects.get(username=request.user.username)
        user_secrecy = user_xtra_auth.secrecy
    newsmanager.update_secrecy(user_secrecy)
    return render(request,'news/index.html',{'data':newsmanager.data, 'news_errors':newsmanager.errors})

def account(request):
    # This is the account view. It is devided
    # into super-user and regular user accounts.
    # In this Mandatory Access Control system,
    # super-users are the security officers that
    # assign secrecy levels to users.
    # The user account page is for designating the
    # secrecy of the news items (and creating news
    # items
    if not request.user.is_authenticated:
        return redirect('/register/')

    elif request.user.is_superuser:
        return admin_account(request)

    else:
        return user_account(request)

def admin_account(request):
    users = UserXtraAuth.objects.all()
    if request.method == "GET":
        form = UpdateUserForm()
        return render(request, 'news/update_users.html', {'form':form, 'users':users})
    elif request.method == "POST":
        form = UpdateUserForm(request.POST)
        if form.is_valid():
                user_auth = UserXtraAuth.objects.get(username=form.clean()["update_user_select"])
                user_auth.secrecy = form.clean()["update_user_secrecy"]
                user_auth.tokenkey = form.clean()["update_user_token"]
                user_auth.save()
                form = UpdateUserForm()
        return render(request, 'news/update_users.html', {'form':form, 'users':users})

def user_account(request):
    # STUDENT TODO:
    # This is the view that handles the User account page
    # where news items are created and news items can be
    # assigned a different classification level.
    # Currently, a user can see all news items. You
    # need to change this to follow the "Simple Security
    # Property" and the "* Property" of Bell Lapadula.
    # NOTE: "data" is populated in three different places
    # in this function.
    data = []
    user_auth = UserXtraAuth.objects.get(username=request.user.username)

    if request.method == "GET":
        all_queries = NewsListing.objects.all()

        create_form = CreateNewsForm()
        update_form = UpdateNewsForm()

        update = all_queries.filter(secrecy=user_auth.secrecy)
        update_form.fields['update_news_select'].queryset = update

        for q in all_queries:
            if q.secrecy == user_auth.secrecy:
                data.append(q)
        return render(request,'news/update_news.html', {
            'create_form':create_form,
            'update_form':update_form,
            'data':data,
            'user_auth':user_auth})
    elif request.method == "POST":
        bad = False
        all_queries = NewsListing.objects.all()
        create_form = CreateNewsForm()
        if "create_news" in request.POST:
            create_form = CreateNewsForm(request.POST)
            user_auth = UserXtraAuth.objects.get(username=request.user.username)
            create_form.user_secrecy = user_auth.secrecy
            if create_form.is_valid():
                clean_data = create_form.clean()
                news_listing = NewsListing(
                    queryId = random_key(10),
                    query = clean_data["new_news_query"],
                    sources= clean_data["new_news_sources"],
                    secrecy= clean_data["new_news_secrecy"],
                    lastuser= request.user.username)
                news_listing.save()
                for q in all_queries:
                    if q.secrecy == user_auth.secrecy:
                        data.append(q)
                newsmanager.update_articles()
            create_form = CreateNewsForm()
            update_form = UpdateNewsForm()
            update = all_queries.filter(secrecy=user_auth.secrecy)
            update_form.fields['update_news_select'].queryset = update
        elif "update_update" in request.POST or "update_delete" in request.POST:
            update_form = UpdateNewsForm(request.POST)
            user_auth = UserXtraAuth.objects.get(username=request.user.username)
            update_form.user_secrecy = user_auth.secrecy
            if update_form.is_valid():
                clean_data = update_form.clean()
                to_update = NewsListing.objects.get(queryId=clean_data["update_news_select"])
                if "update_delete" in request.POST:
                    to_update.delete()
                else:
                    to_update.query = clean_data["update_news_query"]
                    to_update.sources=clean_data["update_news_sources"]
                    to_update.secrecy=clean_data["update_news_secrecy"]
                    to_update.lastuser=request.user.username
                    to_update.save()
                for q in all_queries:
                    if q.secrecy == user_auth.secrecy:
                        data.append(q)
                newsmanager.update_articles()
            create_form = CreateNewsForm()
            update_form = UpdateNewsForm()
            update = all_queries.filter(secrecy=user_auth.secrecy)
            update_form.fields['update_news_select'].queryset = update
        return render(request,'news/update_news.html', {
            'create_form':create_form,
            'update_form':update_form,
            'data':data,
            'user_auth':user_auth})


def register_view(request):
    # This is the register view for creating a new
    # user. Users are initially assigned a secrecy level
    # of 0.
    if request.user.is_authenticated:
        return redirect('/')
    elif request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.clean()["username"]
            newuser = UserXtraAuth(username=username, secrecy=0, tokenkey="")
            newuser.save()
            return redirect('/login/')
        else:
            return render(request, 'registration/register.html', {'form':form})
