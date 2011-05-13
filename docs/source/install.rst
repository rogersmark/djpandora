Installation
==================

First you'll need to install `PyPandora <https://github.com/amoffat/pypandora>`_. That will handle all of our Pandora calls for us. In order to install that module, you'll need the `FModEX <http://www.fmod.org/index.php/download>`_ libraries. Download the package for your system, and instal that. Afterwards, you should be able to::

    pip install -egit+git@github.com:f4nt/pypandora.git#egg=PyPandor

We also assume that you have a working Django installation as well. Then you'll install ``DjPandora`` one of a couple possible ways::

    pip install -egit+git@github.com:f4nt/djpandora.git#egg=DjPandora

Or you can clone the repository yourself and do the usual::

    python setup.py install

Whichever you prefer should get you taken care of. Afterwards, you'll want to add ``djpandora`` to your INSTALLED_APPS Django setting. Finally, you'll want to add 4 new settings to your settings.py configuration:

    * PANDORA_USER - Your Pandora username
    * PANDORA_PASS - Your Pandora password
    * PANDORA_RPC_HOST - Host your XMLRPC server is running on, default should be 'localhost'
    * PANDORA_RPC_PORT - Default should be 8123.

Now you'll want to sync your database to build the ``DjPandora`` database tables. If you're using South, you can use its migrate command instead. Then we'll need to run a few quick commands. First of all, we need to start the XMLRPC server that talks to Pandora::

    ./manage.py start_rpc_server

That starts up our RPC server, now we can communicate with Pandora. We'll want to initialize our station list in Django now, and we have another management command to do just that::

    ./manage.py build_stations

This command goes to Pandora, gets our list of stations, and creates records for each of them. You'll want to go in via the Admin in Django, or to a SQL shell, and mark one of these station's "current" attribute as True. This will seed our first station as the one that should be playing. In the future, that'll be user controlled. Once you have a station marked as "current", we can perform the final step::

    ./manage auth_rpc_server

That will authenticate with Pandora, and start playing the music. Now your office is ready to control Pandora as a group!

One final thing you may want to do is setup a cron job for keeping your station list up to date. Here's an example::

    30 * * * * /usr/bin/python /path/to/your/project/manage.py build_stations