# UT-Austin CS 361S Minilab 5 - HTTP

|||
|---|---|
| Minilab: | 6 - Cookies |
| Class Assigned: | 11/08/2021 |
| Points: | 50 |

In this lab, we will do in-class exercises to play around with cooikes
and two attacks called "Cross-Site Scripting" attacks and "Cross-Site
Request Forgergy" attacks.

## Setup

You only need a Python 3, a browser, and your computer's IP address.
I have uploaded a script called "cookie_test1.py" into this folder for your use.

## Introduction

As I have stressed repeatedly, HTTP is a sessionless protocol. The only way
it can tie together different HTTP requests is from values known as cookies.
These are session identifiers in one form or another.

## The Test Webserver

It would take too long in this write-up to explain all of the cookie_test1.py.
The professor will explain it in class. Please be prepared to go through the 
code, run the code, and so forth.

## Setting and Reading a cookie

Take a look at the code in cookie_test1.py. There are a couple key pieces.
First, take a look at the `render_page` method:

    def render_page(self):
        """Respond to a GET request."""
        if "cookie" in self.headers:
            self._cookie = self.headers["cookie"].split("=")[1]
            self._session = connections.get(self._cookie, None)
            print("Render page with cookie={}".format(self._cookie))
        else:
            print("Render page with no cookie")
            
This is the handler for each page. The very first step in the code
is an examination of the incoming HTTP request header to see if there
is a cookie. If there is, it uses that cookie to look up *state* information.

But how did the cookie get set in the first place? Take a look at this line
in the `_handle_login` method:

    headers["Set-Cookie"]="session="+self._cookie
    
This is setting the *outgoing* HTTP response cookies on the login page. Once
a user logs in, the code associates a new random cookie with session data.
The `Set-Cookie` header tells the browser to use this cookie with all future
connections to this domain.

It's important to understand that cookies are domain specific. So our first
exercise is to run the server for 127.0.0.1 as well as your other IP address.
In one terminal, launch cookie_test1.py without arguments:

    sudo python3 cookie_test1.py
    
In another terminal, use the "--host" argument to set the IP address to the
other address for your system. For example, if your address was 10.0.0.4,
you would do this

    sudo python3 cookie_test1.py --host=10.0.0.4
    
Now, with your browser, visit both 127.0.0.1 and 10.0.0.4. It should show you
the headers it receives each time. The headers may be more or less the same. But now
we will login. Browse to `127.0.0.1/login` and `10.0.0.4/login`. There will be a submit
button and form at the bottom. There is no password. Put in a different name into each
browser window and click "login." You should see in each of the follow-up windows that
the headers from your browser show different cookies (and different logged in users) for
each window.

Take a screenshot of your two windows to show logging in with different users.

## More session work... transfering money

To simulate transfering money, you can browse to `127.0.0.1/transfer` and the other window's
equivalent. You can put in a name here (no value, it's just a name here) and it will now list
that as someone money was transferred to. Again, you can see this is different for each window.

## Hacking the system. XSS First

Cross Site Scripting (XSS) is where you get a user to run bad Javascript (or equivalent) in
their logged-in web session somehow. In our example, we're going to do it with the transfer
button. Go to the transfer screen and put this in for the person to transfer to:

   <script>alert('hacked');</script>
   
This will immediately cause your browser to pop up a dialog box saying hacked. Close the
box (click OK) and try visiting any page. It will keep popping up each time. Why will
be discussed in class. Please show a screenshot shoing the pop-up box AS WELL as the
script in the transfers list.

## Hacking the system. CSRF Second

**RESTART YOUR SERVERS** to clear the XSS mess. Login to both.

The second attack is to show how an adversary can get you to do what is called a 
Cross-Site Request Forgery. In your browser NOT pointed to 127.0.0.1, visit 
`<your other address>/csrf`. See what happens. This will be discussed in class
but for purposes of submission, please submit a screenshot of the new transfer
that shows up in your **127.0.0.1** tab.

## Additional Discussion

We may use this test program in other class periods. Depending on the time in
today's class, the professor may ask for an additional test or two. However,
nothing else will be required for submission.


## Submission
Assemble the screenshots into a word document or
other such file (PDF is fine) and submit to the TA.

## Grading
This minilab, like all other minilabs, is pass fail. We are showing
you literally how to do everything. The class will be recorded. If
you missed it, please submit as soon as possible. This minilab is
designed to help you with the next lab.

    