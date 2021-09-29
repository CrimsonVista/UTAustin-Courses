import setuptools


long_description = """
This is a TLS front-end for two kinds of proxying. The first
is proxying to a non TLS server. So, e.g., an HTTP server that wasn't
built with TLS support.

The second is a SOCKS proxy that can transparently proxy both 
HTTP and HTTPS.
"""

setuptools.setup(
    name="2021sp_cs361s_lab3",
    version="0.0.1",
    author="Seth Nielson",
    author_email="seth@crimsonvista.com",
    description="CS 361S Lab 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CrimsonVista/UTAustin-Courses/2021sp_cs361s/labs/lab3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
    
    install_requires=[
        'scapy',
        'cryptography'
    ]
)