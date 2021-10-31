from django.shortcuts import render

# Create your views here.

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import NewsListing, UserXtraAuth
from .forms import UpdateUserForm, CreateNewsForm, UpdateNewsForm
from .oauth import OAuthClient

from django.contrib.auth import login
from django.conf import settings
from django.core.exceptions import BadRequest
import json, random, string, urllib, requests

key_char_set = string.ascii_letters + string.digits

def random_key(keylen):
    return "".join([random.choice(key_char_set) for i in range(keylen)])

class NewsApiManager:
    def __init__(self):
        self.secrecy = 0
        # Initializing API KEY
        self.errors = []
        self.data = []
        #self.update_articles()
        
    def update_articles(self):
        all_queries = NewsListing.objects.all()
        all_results = []
        self.errors = []
        for q in all_queries:
            # STUDENT TODO:
            # Currently, all queries are returned with out
            # respect to secrecy level. You need to implement
            # the "Simple Security Property" and the "* Property"
            # (of the Bell Lapadula model).
            # 
            # the current secrecy of the viewer is in "self.secrecy"
            # the secrecy level of the query is in "q.secrecy"
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
    return render(request,'news/index.html',{'username':request.user.username,'data':newsmanager.data, 'news_errors':newsmanager.errors})
    
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
        all_queries = NewsListing.objects.all()
        for q in all_queries:
            data.append(q)
        return render(request,'news/update_news.html', {
            'create_form':create_form,
            'update_form':update_form,
            'data':data, 
            'user_auth':user_auth})
    elif request.method == "POST":
        bad = False
        if "create_news" in request.POST:
            create_form = CreateNewsForm(request.POST)
            user_auth = UserXtraAuth.objects.get(username=request.user.username)
            create_form.user_secrecy = user_auth.secrecy
            if create_form.is_valid():
                clean_data = create_form.clean()
                news_listing = NewsListing(
                    queryId = random_key(10),
                    query = clean_data["new_news_query"],
                    sources=clean_data["new_news_sources"],
                    secrecy=clean_data["new_news_secrecy"],
                    lastuser=request.user.username)
                news_listing.save()
                all_queries = NewsListing.objects.all()
                for q in all_queries:
                    data.append(q)
                newsmanager.update_articles()
                create_form = CreateNewsForm()
                update_form = UpdateNewsForm()
        elif "update_update" in request.POST or "update_delete" in request.POST:
            update_form = UpdateNewsForm(request.POST)
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
                all_queries = NewsListing.objects.all()
                for q in all_queries:
                    data.append(q)
                newsmanager.update_articles()
                create_form = CreateNewsForm()
                update_form = UpdateNewsForm()
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

# Configuration
GOOGLE_CLIENT_ID = "" #STUDENT TODO
GOOGLE_CLIENT_SECRET = "" #STUDENT TODO
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

# OAuth 2 client setup
client = OAuthClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def oauth_view(request):

    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Generate an anti-forgery state token with length 30 (variable)
    # Use the random_key() function
    #STUDENT TODO : START
    
    #STUDENT TODO : END

    # Create the authorization request uri
    # Use the client.prepare_authorization_request_uri() function
    # Pass in ["openid", "email", "profile"] as the scope
    #STUDENT TODO : START
    
    #STUDENT TODO : END

    return redirect(request_uri)

def oauth_callback_view(request):

    # Get the anti-forgery state token from the callback
    # and compare with the token already generated
    # Raise an error if their is a mismatch
    # Hint : Check request.GET to get parameters of the GET request
    #STUDENT TODO : START 
    
    #STUDENT TODO : END

    # Get authorization code Google sent back to you
    # Hint : Check request.GET to get parameters of the GET request
    #STUDENT TODO : START
    
    #STUDENT TODO : END

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    # Use client.prepare_token_request() to prepare the token request
    # Send a POST request using the return values of this function.
    # Use the GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET as 'auth' parameters
    # in the post request.
    # Hint : See requests.post to see how to send a POST request
    #STUDENT TODO : START
    
    #STUDENT TODO : END

    # Parse the tokens!
    # Use client.parse_request_body_response() function
    #STUDENT TODO : START
    
    #STUDENT TODO : END

    # Now that you have tokens (yay) let's find the URL
    # from Google that gives you the user's profile information and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]

    # Let us now send a GET request to the userinfo_endpoint.
    # Use the client.add_token() function to generate the headers for the GET request
    # Use requests.get to see how to send a GET request
    # Store the response of the GET request in a variable, userinfo_response
    userinfo_response = None
    #STUDENT TODO : START
    
    #STUDENT TODO : END

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    # Hint : Access the information using userinfo_response.json()
    # Check the email_verified, email and given_name parameters
    # and store that information to create/retrieve an entry in your database
    #STUDENT TODO : START
    
    #STUDENT TODO : END

    # Check if the user with the given username already exists in the 
    # UserXtraAuth, using UserXtraAuth.objects.filter(username = ...).exists()

    # If the user is already present, retrieve their information from the database
    # and store it in the userextraauth variable. Additionally, also populate the
    # user variable through User.objects.get(username = _)

    # If the user, doesn't already exist in the database,
    # Create a user in your db with the information provided
    # by Google.
    # 1. To add to UserXtraAuth model, use userxtraauth.save()
    # 2. To add to User.objects, use User.objects.create_user()
    user = None
    userxtraauth = None
    #STUDENT TODO : START
    
    #STUDENT TODO : END

    # Begin user session by logging the user in
    # The user here can be fetched via User.objects.get(username = _)
    login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])

    # Print all oauth variables
    # All the variables should be populated correctly
    client.print()

    # Send user back to homepage
    return redirect(index)
