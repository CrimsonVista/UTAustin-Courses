# Lab5: Authentication Using OAuth 2.0

|||
|---|---|
| Assigned | 2021-11-01 |
| Due: | 2021-11-16 |
| Points | 100 |

## Overview
This lab is designed to teach you a little bit about 
*authentication* using OAuth 2.0. You might have already come across this when you use "Login with Google/Facebook/Github" etc. on many websites.

OAuth 2.0 is a framework where a user (in this case, you) of a service (such as Google/Facebook/Github etc.) can allow a third-party application (in our case, the newsapp Web application) to access their data hosted in the service without revealing their credentials to the application. In this setting, the application is referred to as the "Client".

OpenID Connect is a framework on top of OAuth 2.0 where a third-party application can obtain a user's identity information which is managed by a service.

In this lab, you are going to build upon your work in lab2 and add a feature so that users are able to login to the application using their Google accounts. Specifically, you would be implementing the instructions [here](https://developers.google.com/identity/protocols/oauth2/openid-connect). The RFC describing the OAuth 2.0 protocol can be found [here](https://datatracker.ietf.org/doc/html/rfc6749).

## Lab Setup

You can use the python3 virtual environment which you set up in lab2 (This means I am assuming that you have the lab2 environment with all the relvant packages installed correctly. If not, please follow the instructions in the lab2 write-up to do so). 

For lab5, you would also require installing an additional package, the instructions for which are provided below.

Assuming that your virtual environment is present in `some_dir`, first activate your environment by using the following command. You would see the name of the environment in your terminal prompt.

	$ source <some_dir>/bin/activate
	(some_dir) $
	
Now, inside this virtual env, install the `requests` package using the following instruction:

    (some_dir) $ pip install requests

The instructions to run the Django WebApp remain the same as that in lab2.

In the class git repo, you will find the start files for this lab
under lab5/newsapp. For this lab, you would be editing the following files : 

1. views.py
2. oauth.py

`utils.py` contains some utility functions that might come handy in your implementation.

Additionally, you would also need to set up a project in the [Google API Console](https://console.developers.google.com/) to create OAuth credentials for Google.

1. Go to the [Google API Console](https://console.developers.google.com/).
2. From the projects list, select a project or create a new one.
3. Select the `Credentials` tab on the left
4. Click on `+ Create Credentials` then select `OAuth client ID`.
5. Select `Web Application` as the application type for your project and enter any additional information required. You can find more details on this additional information [here](https://support.google.com/cloud/answer/6158849?hl=en#zippy=). Please contact the TA incase of any problems.
6. If this is your first time creating a client ID, you can also configure your consent screen by clicking Consent Screen. (The [following procedure](https://support.google.com/cloud/answer/6158849?hl=en#userconsent) explains how to set up the Consent screen.) You won't be prompted to configure the consent screen after you do it the first time.
7. While selecting scopes, take care to select only the following non-sensitive scopes - ./auth/userinfo.email, ./auth/userinfo.profile & openid (you can select more if you like, but it's not required for this assignment).
8. Click Create client ID.
9. After creating the client, in the redirect URI, put in `http://127.0.0.1:8000/oauth/callback`.
10. Copy the Client ID & Client Secret in `views.py` and assing to the `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` variables.

If for any reason, you are unable to create the Client ID and Client Secret through the above instructions, please contact the TA for assistance.

## Codebase Description

The Google OpenID Connect documentation linked previously essentially describes what we are going to implement in this lab. We are going to implement the Client side of the OAuth protocol for authenticating a user for our newsapp Web Application.

The different steps are :

1. Creating an anti-forgery state token.
2. Sending an authentication request to Google on their authorization endpoint.
3. Confirming the anti-forgery state token received on redirection.
4. Extracting the authorization code that Google sent back via the callback.
5. Preparing and sending a request to the token endpoint to get the access token.
6. Parsing the access token, and sending a request to the user info endpoint to get user information.
7. Creating a user in our database, if not already existing, using the information
provided by Google.
8. Logging in the user into the Web Application and redirecting to the index page.

Detailed instructions to complete these steps are provided in the code-base along with prompts where you have to write code. The `oauth.py` file implements the various functions related to creating and parsing the requests received and sent during the protocol. It implements the `OAuthClient` class, an instance of which is created and used in `views.py`.

In `views.py`, you would find 2 new views implemented - `oauth_view` and the `oauth_callback_view`. If you see the `newsapp/urls.py` file, you would find the urls which are being matched corresponding to these views. The first view becomes active when the `Login With Google` link is clicked on the `Sign-In` page. The second view is used to handle the GET request sent back by Google.

The following images denote the sequences of screens that you should see during the course of implementing this assignment. 

1. ![The first screen on clicking the Sign-In button at the top](images/screen1.png?raw=true "The first screen on clicking the Sign-In button at the top")
   *The first screen on clicking the Sign-In button at the top*
3. ![The second screen which appears after clicking the Login with Google](images/screen2.png?raw=true "The second screen which appears after clicking the Login with Google")
   *The second screen which appears after clicking the Login with Google* 
5. ![The third screen which appears after signing in with Google. You should see your name after Welcome.](images/screen3.png?raw=true "The third screen which appears after signing in with Google. You should see your name after Welcome.")
   *The third screen which appears after signing in with Google. You should see your name after Welcome.*
7. ![The fourth screen which appears after logging out.](images/screen4.png?raw=true "The fourth screen which appears after logging out.")
   *The fourth screen which appears after logging out.*

## Submission and Grading

Each student must make their own submission.

Compress the entire lab5 directory as a .zip file (UT-EID.zip) and upload it on Canvas (Assignments > Lab 5 : Authentication Using OAuth 2.0).

To receive full credit for the lab, you must complete all the parts successfully and all the variables printed through `client.print()` should be correctly populated. On successfull completion, you should see your name in the Welcome message.

To receive 80% credit, your submission must successfully reach the third screen after successfully going through the second screen and logging in to your Google account. It is alright if your name doesn't appear in the Welcome message and the variables printed through `client.print()` don't appear correctly populated.
