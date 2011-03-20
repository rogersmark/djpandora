.. DjPandora documentation master file, created by
   sphinx-quickstart on Sat Mar 12 12:51:01 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DjPandora's documentation!
=====================================

Contents:

.. toctree::
   :maxdepth: 2

   install
   features

Introduction
=====================================

DjPandora is an application that interfaces with ``pypandora``. The premise is to allow a group of people to control a single Pandora installation. The idea came about as a way for our office to control the office Pandora radio setup. This will allow users in the office to vote on songs, stations, and so on to control Pandora as an overall group.

In our office, we have a central computer that exists to play music for the office. To control it, we'd VNC in and like/dislike stations, skip songs, or whatever. The problem with this is that it requires one person to assert their musical tastes on the entire group. Inevitably what happens is you end up with a stereo playing, and everyone in the office wearing headphones. With this, every station and song is voted on by the users. 

This project uses ``pypandora``, which is an API wrapper of Pandora heavily inspired by `pianobar <https://github.com/PromyLOPh/pianobar>`_. PyPandora runs an XMLRPC server that ``DjPandora`` talks to in order to control it. We also provide a simple, clean interface for users to use to interface with. 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. automodule:: djpandora
   :members:

