# Lab1: Authentication and Authorization

|||
|---|---|
| Assigned | 2021-09-15 |
| Due: | 2021-09-29 |
| Points | 100 |

## Overview
This lab is designed to teach you a little bit about 
*authentication* and *authorization*. We will also learn
a little bit about Multi-Level Security  (MLS), Bell Lapadula,
Mandatory Access Controls, and the associated security 
properties ("simple security property", and "star property").

You should make sure you are familiar with the assigned
readings related to these concepts.

The fictional scenario for this lab is "Open Source
Intelligence", or OSINT (see, e.g., [this discussion](
https://www.recordedfuture.com/open-source-intelligence-definition/)).
This is a real thing used by real intelligence agencies
including United States intelligence services. It has been
estimated that 85 percent of US intel is derived from
public (open source) sources.

Although the information comes from public sources, the analysis
of the information is almost always confidential and secret. Even
the fact that data is being gathered about a topic is a secret and
should not be disclosed without clearance.

In this lab, you are going to build a news aggregator with 
a secrecy level attached to each query. Moreover, the users of the
system will also have a secrecy level assigned. You will modify
the news aggregator to follow the Bell Lapadula model and enforce
what is known as No Read Up (NRU or the simple security property)
and No Write Down (NWD or the \*-property).

You will also learn a little bit about two-factor authentication.
We will examine some principles related to something-you-know
authentication (passwords) and a simulation of something-you-have
(a fake RSA token).

## Lab Setup

This lab requires the use of python and a python web framework
library called Django. You should be able to use this setup in
WSL, Linux, or Mac. However, I have not tested Mac. 

From whatever environment, start from command shell/prompt.

First, create a python3 virtual environment, then activate it. You
should see the name of the environment in the prompt

    $ python3 -m venv <some_dir>
	$ source <some_dir>/bin/activate
	(some_dir) $
	
Now, inside this virtual env, install the dependencies:

    (some_dir) $ pip install wheel django cryptography
	
For Ubuntu, I have recently had problems installing cryptography.
If it fails with some error about needing "setuptools_rust", 
make sure you have an updated pip. If that doesn't work (it didn't
for me), install cryptography version 3.3.2.

    (some_dir) $ pip install cryptography==3.3.2

In the class git repo, you will find the start files for this lab
under lab2 newsapp. You should copy these files to your repository
and make whatever edits you need.

Change to the newsapp directory in your repository and run the following 
command to configure the site secret:

```
python generate_secret.py
```

While not required for the lab, you might want to look at what this does
and try to guess why it is dones this way.

Next, set up the tables the webserver will use to display newslistings.

```
python manage.py migrate --run-syncdb
```

Also, 

Once they are set up, you should register a superuser for the web server using
```
python manage.py createsuperuser
```

Now that the web tables and superuser is set up, you can finally run the webserver app using

```
python manage.py runserver
```

The website should launch on your localhost`s port 8000.

## Newlister App

The App, as you get it out of the github, is functional. You can
create accounts, assign secrecy, and create news items. Here is a
quick walkthrough of the functionality.

First, make sure you created a superuser as described in the setup.
If you haven't already done it, this is the command line:

```
python manage.py createsuperuser
```

Once you have the superuser setup, launch the site

```
python manage.py runserver
```

Now browser to 127.0.0.1:8000. You should see a fairly blank page
that says "Newslist App" and has at the header three tabs: 

1. News List
2. Register
3. Sign In

You can sign in as the super user, but the super user doesn't actually
have a secrecy level and can't actually create news items. The super
user is supposed to be the security officer. The sole job of the super
user is to assign secrecy levels to registered users. There just aren't
any registered users yet.

So, the next thing to do is register a user. Go to the "Register" tab
to create a new user. You will need a username and a password. Please be
aware that this lab was created in a hurry and the error messages are
terrible. Django will check your password for some basic checks, such as
the password must be long enough, but if you do a bad password, it gives
the error "Your username and password didn't match." If you see this, it
simply means it didn't like the password you tried to use.

If you successfully register a user, it will take you to a sign-in page.
You can sign-in as either the super user or the newly created user. If you
sign-in as a user, you can go to the "Account" tab to create a news item.
Give it a try and then go to the newslist. Note that the news list will show
news items created from ALL users. So maybe register a couple of users, create
news items for each one. You should see ALL of these in the news list.

You can also sign-in as the super user and go to the "Account" tab to assign
each user a "token key" and a secrecy level. While the data is saved, it is
currently not used. You will be modifying the code to enforce the 
Bell Lapadula model (no read up, no write down) on the news items and to
add-in two-factor authentication (simulated, anyway) for all users with a 
non-zero secrecy level.

This is the start of your lab.

## Part One: Multi-level Security and Bell Lapadula

As you know from your reading, Bell Lapadula introduced
a security approach with two policies:

1. No Read Up
1. No Write Down

Within most governments, information is carefully controlled
(whether or not the control of information by a government is
*ethical* is outside the scope of the class). Within the US
government, there are a few common classifications such as

1. Sensitive But Unclassified (SBU)
1. Secret
1. Top Secret

Information is also marked with classification levels. Bell
Lapadula's first property (No Read Up) is probably intuitively
known amongst most people. This means that you cannot
read information marked with a higher classification than you
possess. 

But most people do NOT know that the other side of this is
"No Write Down." This means that you cannot write to a lower
classification than your clearance level.

Your first assignment in this lab is to modify the newslisting
app to enforce both NRU and NWD. The source code is not complicated
and the places that require modification are marked with "STUDENT TODO"
tags.

But you will need to think carefully about what NRU and NWD mean
in practice. What constitues reading? What constitutes writing?
We will release concrete expectations before the lab is due so you
don't have to guess at the final output. But we want you to think
this through yourself before we tell you what to do.

Please note that users are first registered in the system with a 
secrecy level of 0. The super use can assign them a higher 
secrecy level. However, although not strictly a Bell Lapadula
policy, for this lab you should not allow the super user to
reduce a user's secrecy level.

## Part Two: Hacking Passwords

Django does a very good job of storing passwords in a reasonable and
secure manner. You can read a bit about password storage 
[here](https://docs.djangoproject.com/en/3.1/topics/auth/passwords/).
The key point is that the passwords are stored hashed with an
algorithm called PBKDF2 and a lot of iterations.

We are going to learn a little about how attackers "crack" passwords.

Your first assignment is to find the database that holds all the passwords.
If you look in your newsapp directory, you will see an sqlite3 database.
You can query these databases directly without going through the app. 
By querying the database, you can get a list of all the databases and figure
out which one stores the passwords.

You can use an sqlite3 program or you can use Python and the sqlite3 module.
For example, take a look at this 
[stack overflow discussion](https://stackoverflow.com/questions/305378/list-of-tables-db-schema-dump-etc-using-the-python-sqlite3-api) about searching
for tables. The second answer from the top shows Python code to query for
all tables.

Between the article about how Django stores passwords and the information
you extract from the sqlite3 database, you should be able to figure out how
your passwords are stored in terms of algorithm, iterations, and salt.

Before we explaine details about algorithm, iterations, and salt, let's
first identify the type of problem we're trying to solve.

When an attacker breaks into, or compromises, a website, they often steal
password lists. For this reason, the passwords are not usually stored in
plaintext, but in a hashed form.  There are a number of reasons for 
doing this. Most of the time, for example, the password is going over
the wire in cleartext, but is encrypted by TLS. Thus, even if an attacker
steals the hash, (s)he still cannot login as the user. Let's walk through this.

1. User logins in with password "password"
2. Password "password" is sent encrypted over TLS; attacker cannot see it
3. Attacker breaks into website and finds password is stored PBKDF2 hashed
4. Attacker still doesn't know password is "password", still can't login

I have heard that some applications do the hashing on the client side (e.g.,
browser). If this be the case, the attacker could replay the hash to get
logged in on the website. However, the attacker still doesn't know the plaintext
password. So as soon as the website is aware of the compromise, they can
have the user reset the password. Even if the user picks the same password,
the website can change the *salt* meaning that the hash has changed too.
The attacker can no longer get into the user's account.

But another reason for storing the user's password hashed is to prevent the
attacker from breaking into their account on *other* websites. Unfortunately,
users re-use passwords across websites and this means that if you can figure
out a passwored on one website, you have probably figured out that same password
on other websites.

By storing the cleartext password hashed, it is harder for the attacker to
learn a user's (probably re-used) password.

What can the attacker do? Well, unless there is a vulnerability with the hashing
algorithm, they have to resort to brute-force or something similar. Basically,
they have to possible passwords (e.g., "password"), run it through the same
algorithm and see if it comes out the recorded hash.

Algorithms like PBKDF2 make this much harder for the attacker by using an
algorithm that is repeated thousands of times making it take imperceptibly longer
for the user (who only has to run the algorithm once), but many times longer
for the attacker (who has to re-run the algorithm on every single word tested).

Let's return to the three major components and define them:

1. Algorithm - this is the calculation used to convert the password to a hash.
PBKDF2 is a commonly used algorithm
2. Iterations - most password derivation algorithms permit the algorithm to be
run a configurable number of times. The more iterations the longer it takes to
convert a password to a hash.
3. Salt - a public, random value that is used to produce unqiue hashes. If the user picks
the password "password" without a salt, the hash is the same every time and across
every website (that also doesn't use a salt, and uses the same number of iterations).
This also means that two users that pick the same password would end up with the same
hash (leaking information to the attacker). By using a salt, each user's hash can
be unique regardless of which password is picked.

But even with all of these protections, an attacker can still get out well-known
passwords. These protections prevent an attacker from literally trying every single
combination ("a", "b", ... "z", "aa", "ab", ...), and from a dictionary of too many
words. But really common passwords (e.g., "password"), can still be guessed 
very quickly.

You job for this part of the assignment is to write a password cracker for the website.
Please create the file in your "newsapp" directory (the same directory with
manage.py) and call it "cracker.py".

Your password cracker is going to do two things. It is going to crack passwords
in Django if they are really, really common. It is also going to crack passwords
passed in at the command line by brute force if they are "weak". Let's explain each
one.

If your "cracker.py" file is called with NO arguments, it should do the following thing:

1. Open the sqlite3 database for the newsapp. Your app can assume it is in the
same directory.
1. Extract all of the stored password hashes from database tables.
1. Take each of the most common passwords from Wikipedia's article 
"List of the most common passwords." Last I checked, 2020's Nordpass was
at the top. Use that list. (If it changes by the time you read this, contact me).
Run it through the same algorithm, with the same salt, with the
same number of iterations.  Identify if the hashes are the same
(e.g., you've cracked that password).
1. For cracked passwords, report at the command line `<user>,<password>`
(this should be the only output with one pair per line).

Remember, Django passwords will be stored in the database as

```
<algorithm>$<iterations>$<salt>$<hash>
```

You can assume that algorithm will always be PBKDF2, but you should 
check the iterations and salt for each entry. We will test your cracker.py
file on databases you did not create and may not follow the default
django rules.

To run your own PBKDF2 algorithm, you need to use the Python cryptography
module. It's pretty straightforward and you should be able to just
follow the example in the [documentation](https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/).
Please note that the hash stored in the Django database is base 64 encoded,
so you will need to import "base64" and use "base64.b64encode" and "base64.decode"
to switch back and forth.

Also, to get the cryptography module, use pip from within your pipenv virtual environment:

```
pip install cryptography
```

Your "cracker.py" file should also optionally take a single command line
argument. If a command line argument is passed, it should be a Django
password database entry with the same format as above. Specifically, 
the command line parameter should be:

```
cracker.py <algorithm>$<iterations>$<salt>$<hash>
```

In this case, you should not consult the database file at all. Rather, 
you should check if "iterations" is 1. If it is any other value, 
report:

```
Cannot brute-force password in time.
```

If "iterations" is 1, you should run through every possible combination
of passwords that is between one and four characters, where each character
is a lowercase letter (a-z). That is, you should test the possible passowrd
'a', 'b', 'c'... and then 'aa', 'ab', 'ac', and so on through 'zzzz'. If
the password + salt matches, your cracker.py should report

```
Password cracked: '<password>'
```

Otherwise, it should report

```
Password not cracked.
```

## Part Three: Fake RSA Token

Your final assignment for this lab is to add in a simulated second
factor authentication to the system. In particular, users with
a secrecy level greater than 0 must use a simulated RSA token
to complete the login process.

You can read about RSA tokens (SecurID) on [Wikipedia](https://en.wikipedia.org/wiki/RSA_SecurID).
Back before everyone had a cell phone, this was the most common 
way to do 2FA. The idea was that you were issued one of these
hardware tokens. The token would display a new code every so many
seconds. When logging in, you would have to enter both your password
and the current code.

Internally, the token has a secret number that is used as a seed to
a PRNG. It generates each new code based on the seed. The seed is also
stored on a central server, allowing the server to verify that the
code is correct.

You are going to simulate an RSA token. I have already written all the
logic of the token for you. In your "newsapp" folder is a "fake_token.py"
file that both can be used as the token (generating the codes for your login)
and as the library you will use in your Django app to verify the code.

If you recall, the super user (security officer) can assign a user
a secrecy level and a token ID. The token ID is just a password used
as a seed to the generator. When running "fake_token.py" from the command
line, you can pass the token as the first argument. The utility will continue
to pump out numbers that are updated every 30 seconds or so. Like this:

```
fake_token.py blahblah
5 7539280
30 1609206
...
```

The first number is how many seconds are left before the number changes. If it's
a small number, wait for the next one before logging in. The second number is
the code to put in as the second factor authentication.

In terms of modifying django, you are going to modify the code so that
the user *appends* the fake token code at the end of the password. That is, if
the current code is 111111 and the password is "password", the user would
put in "password111111" into the login box when signing in. 

To modify the code, look at the following file:

```
labs/lab1/newsapp/newsapp/urls.py
```

At the top, you'll see a class called TokenLoginForm. This is the
form that accepts the user's login credentials. What we are going to do here
is *intercept* the password before it's processed. You need to do the following:

1. IF the user's secrecy is > 0
1. Extact the user's token seed. The stub code already has the user auth 
data in "user_xtra_auth"; the seed is "user_xtra_auth.tokenkey"
1. Determine the fake token value. You should be able to import the
fake token code directly ("import fake_token"). See if you can figure out
the rest from looking at the code. It's straight forward
1. If the user's password doesn't end in the fake token code, raise a validation
error (the first argument to this error should be "Invalid Token Code").
1. Otherwise, strip off the fake token code from the password so Django
can do the normal password verification

As explained in the comments of the stub code, the password should be in the
"cleaned_data" data structure. Like this:

```
self.cleaned_data['password']
```

You will notice that there is a call to "super().clean()" at the end. This
is where the normal password validation takes place, so you need to 
have the password fixed up before that call or it will not have the
correct password.

As a reminder, the super user MUST assign a token when the user's 
secrecy is greater than 0. Also remember that a super user cannot
reduce a user's secrecy level.

If you want to remove a user altogether, the super user can manually
navigate to the `/admin` page. There the SU can see all users and
remove them from the system if necessary.

## Grading

Coming Soon. Autograder under construction
