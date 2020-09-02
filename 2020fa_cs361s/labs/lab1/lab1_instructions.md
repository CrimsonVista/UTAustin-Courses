# Lab1: Authentication and Authorization

|||
|---|---|
| Assigned | 2020-09-02 |
| TA: | 2020-09-21 |
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
To begin open up your Ubuntu VM.  Download the virtualbox image found in the files tab on Canvas to avoid setting up any Python dependencies.

**The provided virtual image's root account password is "root"(you can change this later if you would like).** 

Once inside the image, open the terminal and enter
```
pipenv shell
```
to enter the python virtual environment shell.

If you are using the provided the virtualbox image, your machine should already have this python virtual environment command and all of the python modules needed for running your webserver.  If not, you will need to install pipenv and the modules yourself.

Now git clone the Lab1 web server`s starting files and navigate inside the folder in your terminal.  Run the following command to set up the tables the webserver will use to display newslistings.
```
python manage.py migrate --run-syncdb
```

Also, you need to create a secret for Django by running
```
python generate_secret.py
```

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

Walk Through

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

## Part Two: Hacking Passwords

Coming Soon

## Part Three: Fake RSA Token

Coming Soon
