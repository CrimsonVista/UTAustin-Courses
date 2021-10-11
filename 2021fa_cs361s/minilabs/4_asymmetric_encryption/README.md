# UT-Austin CS 361S Minilab 2 - Networking

|||
|---|---|
| Minilab: | 4 - Asymmetric Encryption |
| Class Assigned: | 10/11/2021 |
| Points: | 50 |

In this lab, we will do in-class exercises to work with asymmetric encryption.
We will learn a little about certificates, public keys, private keys, signatures,
verification, and asymmetric encryption/decryption.

## Setup

You need the same setup from Minilab 3.


## An Introduction to Public Keys

In our previous minilab and class lecture, we used a "symmetric" key to encrypt and
decrypt. It's called "symmetric" because you use the same key to encrypt and decrypt.

In this lab, we will have asymmetric operations when there is a public key that can
be given to anyone (or everyone) and a private key that only the owner should ever have.
Because public keys are often handed out to anyone (or everyone), it is common to encode
them within a "certficate." The certificate has information about the key, what type it is,
and certain validity information like a serial number and valid dates of use.

## Generate a self-signed certificate.

You should have already donw this in Lab 3. But if you didn't, we will re-do it here.
To generate a certificate (which contains a public key) you must first generate a private
key. The following command generates a private RSA key.

    openssl genrsa  -out minilab4.key 2048
    
Keys do not have to end in a .key extension. However, I think this makes the lab more understandable,
so we will go with it for now. Once the key is created, a certificate can be generated using
the private key. NOTE: the certificate will NOT contain the private key, but rather, will contain
a public key derived from the private key.

    openssl req -x509 -new -nodes -key minilab4.key -sha256 -days 160 -out minilab4.pem
    
The .pem extension is used for more than just certificates. PEM is a type of encoding for serialization.
Also, when you run this command, it will ask for some additional metadata interactively. The answers
aren't particularly important.

Once the certificate is generated, we can use the following OpenSSL command to investigate it.

    openssl x509 -in CS361S_Fall2021_CA.pem -text
    
For your first assignment, please take a screenshot of the text. It is a lot of text and may
require two screenshots.

## Loading the certificate and key in Python

We can load the certificate and key we generated in Python to do some public key
cryptography. First, let's load the certificate.

    >>> from cryptography import x509
    >>> with open("minilab4.pem") as f:
    ...   pem_data = f.read()
    >>> cert = x509.load_pem_x509_certificate(pem_data)
    
The `cert` variable is a `Certificate` object. You can find documentation about this
in the Cryptography docs. But for today, we care about extracting the public key
from the certificate.

    >>> public_key = cert.public_key()
    
What can you do with a public key? A lot actually! But let's load the private key first.
Remember, the private key is not in the certificate. We have to load it separately.

    >>> from cryptography.hazmat.primitives import serialization
    >>> with open("minilab4.key", "rb") as f:
    ...   private_key = serialization.load_pem_private_key(f.read(), password=None)
    
Ok, we now have loaded our private key and corresponding public key. We can start
some asymmetric operations!

## Signing and Verifying a Signature

For this part we will be following the Cryptography documentation found at
[https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#signing](
https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#signing).

As shown in the signing example, we use the RSA private key to sign some data.

    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    message = b"A message I want to sign"
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
A signature does not encrypt the data. Unless encryption is also applied, 
the message `message I want to sign` will be sent unencrypted ("in the clear")
along with the signature. The signature does not keep it confidential. The
purpose is to tell use *who* sent the message and whether or not it has
been altered.

To verify a message against its signature, we go onto the signing example
of the documentation. Note, you already have the public key from the certificate
so you do not have to do the first instruction that re-generates the public key
from the private key. Also note that we are skipping pre-hashing examples.

    public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
Try changing the message and re-run the verification. You should see an exception.
Take a screenshot showing that both the correct message validated and an incorrect
message could not be validated.

## Encryption Decryption

RSA also supports an encryption operation. It might seem counter-intuitive, but we
*encrypt with the public key*. The next section of the documentation has the example.

    message = b"encrypted data"
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
Once the message is encrypted, it can be *decrypted with the private key*. This
is shown on the documentation page.

    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

You should verify that `plaintext` is the same as `message`. Encrypt another
message of your own and decrypt it. Take a screenshot of encrypting and decrypting
your own message.

## Submission
Assemble the screenshots into a word document or
other such file (PDF is fine) and submit to the TA.

## Grading
This minilab, like all other minilabs, is pass fail. We are showing
you literally how to do everything. The class will be recorded. If
you missed it, please submit as soon as possible. This minilab is
designed to help you with the next lab.