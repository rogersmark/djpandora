import os
from setuptools import setup, find_packages

setup(
    name = "djpandora",
    version = "0.1",
    author = "Mark Rogers",
    author_email = "f4nt@f4ntasmic.com",
    url = "http://www.f4ntasmic.com",

    packages = find_packages('.'),
    package_dir = {'':'.'},
    data_files=[('.', ['README','MANIFEST.in']),],
    package_data = {
        'djpandora':
        ['templates/*.html',
        'templates/djpandora/*.html',
        'fixtures/*.json'
        ],
    },
    include_package_data=True,

    keywords = "django pandora",
    description = "Pandora control application for your office",
    install_requires=[
    ],
    classifiers = [
        "Intended Audience :: Developers",
        'Programming Language :: Python',
    ]
)
