# Lab6: Web Security

|||
|---|---|
| Assigned | 2020-11-16|
| Due: | 2020-12-02|
| Points | 100 |

## Introduction

For this lab, you will use SQL injection to attempt to dump a database
and extract a "flag". The website is a publicly accessible CTF-exercise
website.

* [Challenge Page](https://ctflearn.com/challenge/88)
* [Vulnerable Server](https://web.ctflearn.com/web4/)

You might be a bit surprised to see that the only thing written on the
challenge page is, "you know what to do."  Even though this exercise is
listed as "easy", you probably have no idea how to even get started if you
haven't done one of these before.

A good place to start is to always look at the HTML code. In real servers,
careless web developers often leave in clues and hints. In CTF servers, 
it's often a good idea to at least check if there's a hint or suggestion.
In this particular case, there's a comment that's useful for getting started.

The next thing to do is to see if you can plugin some SQL that will cause
the list of tables to be dumped. You might have to try a couple of guesses
as to whether this is a MySQL database, an SQLite database, and so forth.
Each one has slightly different underlying layouts. [This] webpage was 
helpful to me in getting started. But please note, the SQL listed there
isn't going to work out-of-the-box. You're going to have to think about
how to shove that into the SQL that's happening in the page already.

How can you know what the page's SQL looks like? YOU CANT! But you can make
good guesses and try it out to see if you're right. For example, how might
a website naively dump form data into an SQL query? Here's a hint... do you
think they might be using quotes? If so, how will that change your approach?

I'm not telling you how to do a lot of this on purpose. I want you to have
to poke and prod a bit. 

## Grading and Pass off

One of the fun things about these kinds of challenges is even the "flag"
isn't always clear. In other words, it may not even be super clear what
it is you're looking for. So I'm not going to tell you initially exactly what
key or value you're supposed to find. You'll hopefully recognize it when you
see it.

If you really can't advance, you can ping me directly for a hint. If you
want to check if you've found it, create an account on ctflearn and submit
what you believe the flag to be. It will tell you if you've solved it
correctly.

Please submit the flag by putting a file in your top level 
github called "ctf_flag_capture.txt". The only contents of this file should
be the ctf flag value. 