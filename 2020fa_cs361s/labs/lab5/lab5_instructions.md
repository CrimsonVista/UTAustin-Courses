# Lab5: Authentication and Authorization

|||
|---|---|
| Assigned | 2020-11-02|
| Due: | 2020-11-16 |
| Points | 100 |

## Introduction

We've talked a little about RSA encryption. Unlike most other
asymmetric algorithms, RSA can encrypt short messages. This
type of encryption is often used for "key transport" wherein 
one party generates a key (or key material) and sends it 
to another party encrypted under the latter's public key. As
it is encrypted under a public key, only the possessor of the 
private key can decrypt it.

However, RSA is vulnerable to a number of different attacks and
RSA encryption isn't safe without *propper* padding.  The padding
used in TLS 1.2 RSA-based ciphersuites is PKCS v1.5. It turns out that
this mode of RSA encryption is vulnerable to a padding oracle
attack.

The name of the discoverer of this weakness is named Bleichenbacher. You
can read his analysis [here](http://archiv.infsec.ethz.ch/education/fs08/secsem/bleichenbacher98.pdf).
WARNING! This paper is very mathematics heavy and somewhat dense. 
Don't be afraid, however. We'll work through it together!

The basic idea behind an "oracle" attack is that you have some kind
of system that will give you some kind of answer to questions
without an explanation of how or why the answer is correct. In this
particular example, the oracle is the padding itself.

You see, RSA encryption and decryption is ignorant of the padding.
That is, the encryption and decryption operations are not dependent
on the padding nor does the padding factor into the encryption and decryption.
This means that you decrypt and remove padding as two separate and
distinct steps, even though most API's (including Python's Cryptography
module) do it in a single step.

The PKCSv1.5 padding has mostly random bytes, but the first two bytes
are 0x00 and 0x02. This is the key to the oracle. Once the RSA decryption
is finished, if you know that the PKCS v.15 is used for padding, the
first two bytes MUST be 0x00 and 0x02. If those are not the first two bytes,
the decryption was unsuccessful (e.g., you don't have the right key).
Thus, you have an oracle that tells you whether the decryption was right or
wrong.

In the real world, the oracle would typically be a server. In the case of TLS,
for example, servers used to report "Bad Padding" as a TLS Alert when the
padding bytes were incorrect. This meant that you could "test" an RSA key to
see if it was correct. If it was not correct, you would get back 
the "Bad Padding" response. Thus, the TLS server was an oracle for telling 
you whether or not you had used the correct key.

Bleichenbacher found a way to use this oracle to repeatedly close in on the
correct key in an iterative fashion. In this lab, we're going to
re-create his attack.

## Setup

We have provided a shell file called `rsa_oracle_attack.py` in the github
repository. This file starts out with a few required utilities that you will
need to do your work. Your lab will require the Python cryptography library,
which you should already have installed. You will also need to install a
working `gmpy2` module for python. The easiest solution is to work in your
Virtual Machine for lab2. I know some of you had trouble with this, but it is
still my recommendation. In any event, the following commands will install
gmpy2 for python 3 on Ubuntu:

  sudo apt-get install python3-gmpy2
  
You can either create a new virtual environment or you can update your existing
environment by copying in the gmpy2 files (symlinks would also be fine):
  
  ln -s /usr/lib/python3/dist-packages/gmpy2-2.0.8.egg-info <venv base>/lib/python3.6/site-packages/
  ln -s /usr/lib/python3/dist-packages/gmpy2.cpython-36m-x86_64-linux-gnu.so <venv base>v/lib/python3.6/site-packages/
  
  
Once installed, you should be able to use the provided code. The key utilities
are the `simple_rsa_encrypt` and `simple_rsa_decrypt` functions that can do a
"raw" RSA encryption. The Python cryptography module correctly refuses to do
something so dangerous, but we need to do the encryption separate from the
padding. These two utilities provide such operations.

I've also provided two helpful `int_to_bytes` and `bytes_to_int` functions.
These are simple wrappers around the regular functions but with certain
parameters (e.g., endianness) already entered. In the case of `int_to_bytes`
it will auto-determine the number of bytes needed, but you can optionally
express the number of bytes required if you wish.

I'm also going to give you a Fake Oracle class that will serve the purpose
of the oracle for the attack. Again, in real life, it would be some kind
of server. But for our local test, it will just be a class that wraps the
RSA private key and returns true if a decrypted ciphertext starts out with
the correct padding bytes.

Beyond these utilities, a base `RsaOracleAttacker` class is provided.

## Your Assignment

As per the Bleichenbacher paper, you need to fill in the methods for the 
various steps of the algorithm: steps 1, 2a-2c, 3, and 4.  Additionally,
there is a utility step called `find_s` that you will also need to complete.
The code includes comments about how these are implemented, but it would
be good to review the paper to see what each one represents.

## Grading and Pass off

We will provide an autograder. We swear it will work this time.