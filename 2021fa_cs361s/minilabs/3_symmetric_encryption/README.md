# UT-Austin CS 361S Minilab 2 - Networking

|||
|---|---|
| Minilab: | 3 - Symmetric Encryption |
| Class Assigned: | 10/4/2021 |
| Points: | 50 |

In this lab, we will do in-class exercises to encrypt data using the Python Cryptography
module. We will also do a little bit of data verification with HMAC.

## Setup

You should already have the Python Cryptography module
installed in your virtual environment for lab 1 and/or lab3. You're welcome
to use one of these environments.
Alternatively, you can create a new virtual
environment in which you install the cryptography module using pip. You can
find instructions for installing the cryptography module in the lab 1 write-up.


## Cryptography

The Python Cryptography module provides various cryptographic operations using
some kind of underlying "engine." Commonly, the engine is OpenSSL, if you've heard
of that.

The documentation is generally helpful. You can find it [here](https://cryptography.io/en/latest/).


## An Introduction to Encryption with AES

We will talk about AES in our next class. For our purposes today, the only things you need
to know are, (1) AES stands for Advanced Encryption Standard (OK, you didn't really need
to know that) and (2) you can think of the AES algorithm as a kind of "black box." This 
black box, once configured with a key, takes a 16 byte (128-bite) number in and spits out
a 16 byte number as output.

*MAIN IDEA*: For any given key you haven't seen before, it is impossible (in practice) to
figure out the output from the input and the input from the output.

                               [ Key ]
                                  |
                                  |
                                 \ /
    [ 16-byte inpu t] --> [ AES BLACK BOX ] --> [ 16-bytes output ]
    
That's the conceptual. Now let's look at the API. Cryptography's symmetric encryption
documentation is found [here](https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/).
You will see an example with AES near the top of the page. Open Python's interactive shell
and walk through it. We haven't explained IV's yet nor modes (like what is CBC), but we'll get 
to it.

Why did the example use "a secret message" as the input? In python run the following:

    >>> len(b"a secret message")
    
The result, as you will see, is 16. Remember how we said AES requires 16-byte inputs? You can give
it more than 16 bytes, but it must be in *multiples* of 16. Try an example of encrypting a message
that is not a multiple of 16 bytes and see what kind of error message you get. You should have noticed
that in the example there was an `update` API and a `finalize` API. What do these two functions do?

For your lab write-up, provide answers to the following questions along with screenshots
that show the tests you did to figure them out:

1. Which one of them throws the error if the message is too short? 
1. What happens if you try multiple`update` calls followed by a single `finalize`? 
1. What happens if you try to call `update` after `finalize`?

## The Mode of Your Declaration...

Congratulations if you recognized the Pride and Prejudice quote!

So let's talk about "Modes." As you saw in the API, you configure the Cipher object with both
an AES algorithm (parameterized by a key) and a mode. The mode in the example was CBC and it was
parameterized with an IV.

A mode, or mode of operation, is a way of *using* the AES algorithm to encrypt data. Remember
the black box diagram from the last section? That's a "raw" usage where you literally just stuff
16 bytes in and get 16 bytes out with no other operations. When an algorithm like AES is used this
way, we say it is the "Electronic Code Book" (ECB) mode. It's called electronic code book because
AES is serving the same purpose as a look-up in a code book. You open the book, give it an
input, and it spits out an output. But there are all kinds of problems with this.

To test this out, we're going to encrypt an image using ECB mode. You will find a file called
"topsecret.bmp" in the minilabs folder. Take a look at it in a viewer to see the image. This
image is saved without *any* compression or other transformations. Basically, every pixel in this
image is encoded as a number in the file. The file also has a small 54 byte header.

    [ 54 byte header ]
    [ 481024 byte image data ]
    
For our test, we are going to create a NEW image file that has the same header but an
encrypted image data body. Notice that, conveniently, the image data is a multiple of 16.

To do the encryption open a Python interactive shell and, as in the previous example, 
load the necessary imports and create a key. You will not need an IV. When you create the
cipher, create it with ECB mode instead of CBC mode.

    >>> cipher = Cipher(algorithms.AES(key), modes.ECB())
    
Next load the data from the image file (the code shown below assumes the image
file is in the current directory):

    >>> with open("topsecret.bmp","rb") as f:
    ...   plaintext = f.read()
    
The output has to be the original, UNENCRYPTED 54 bytes, followed by the encrypted
body of the image.

    >>> encryptor = cipher.encryptor()
    >>> encrypted_body = encryptor.update(plaintext[54:]) + encryptor.finalize()
    >>> encrypted_image = plaintext[:54] + encrypted_body
    
Now, write out the encrypted image file:

    >>> with open("topsecret_encrypted.bmp","wb+") as f:
    ...  f.write(encrypted_image)
    
You can now open the topsecret_encrypted.bmp in a viewer. What do you see? Include
a screenshot of your "encrypted" image in your lab write-up.

The problem with raw mode is that each 16 byte chuck is encrypted individually.
If two inputs are exactly the same the two outputs are exactly the same! (See
the block diagram again to see why). So if there are patterns between inputs
then there will be patterns between outputs.

To solve this problem AES can be used in a "mode" that ties together the blocks
so that the output is "unified" in some way. We'll discuss how CBC works in class
but for now, re-run the experiment above but use CBC mode instead of ECB. Include
a screenshot of your output encrypted using this mode.

## Using Message Authentication Codes
Encryption is used to makde data *confidential* but it doesn't prevent it 
from being changed. The concept of a Message Authentication Code (MAC)
is a code that will tell you if data has been altered. Here's a [link](https://cryptography.io/en/latest/hazmat/primitives/mac/)
to the APIs for MACs in Cryptography's documentation. From this page,
click on the Hash-based (HMAC) operations.

At the top of this document is an HMAC example. Run through it once
to test it out. Note that there is no minimum size requirement
for inputs to an HMAC.

For your last exercise for the lab, take an encrypted message (the simple
`a secret message` from the first example is fine) and do two different
types of MAC operations.

First, do what is called "encrypt-then-mac." For this exercise, encrypt
the data first (any mode is fine) and then compute a MAC and append it
to the end.

Second, do what is called "mac-then-encrypt." For this exercise,
MAC the plaintext, attach it to the message, and then encrypt all the
bytes together. If the data is not a multiple of 16 (if you use HMAC-SHA1),
just add `\x00` bytes to pad it out.

For now, you don't need to actually do the verification tests. For
this report, attach screenshots of creating both versions.

## Submission
Assemble the screenshots into a word document or
other such file (PDF is fine) and submit to the TA.

## Grading
This minilab, like all other minilabs, is pass fail. We are showing
you literally how to do everything. The class will be recorded. If
you missed it, please submit as soon as possible. This minilab is
designed to help you with the next lab.