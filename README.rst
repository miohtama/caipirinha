Miss Caipirinha is an IRC help bot as software as a service. It is designed to be an infrastructure tool for open source communities to make community support discussion (help chat in IRC) more streamlined by
educating people about internet etique, good ways to ask a question and alternative forums to search help.

I wrote this bot because after 10 years of answering the same questions all over again I think the world needs something better.

The bot will auto-reply people who *join the channel for the first time**

* Introduce people to IRC chat and how to ask questions

* Create a simple help page for your project via web UI based on the best practice templates

* Configurable channel specific greetings you can set through web UI

To bot will reply to **all people** joining the channel

* Average answer time at any given moment (based on weekdays daya)

* Other nice statistics

.. :contents: :local:

Usage
--------

Only irc.freenode.net IRC networks chats currently supported. Other chats can be added in the future.

Setup
~~~~~~~~~~~~~~~~~~~

Invite bot to your channel::

    /invite misshelp #yourchannel

If you are a channel operator you can ask for a managment link to access Miss Help channel admin interface::

    /msg misshelp #yourchannel config

Getting rid of it
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can set the bot mode to *quiet* in the admin interface.

However if you are a channel operator you can also get rid of the bot::

    /msg misshelp #yourchannel part

Reseting the bot
~~~~~~~~~~~~~~~~~~~

By default, the bot greets people only when they join for the channel for the first time.

You can reset the known people with the private message command:

    /msg misshelp reset #mychannel

You need to be a channel operator.

Development
-------------

Install::

    sudo port install mongdodb

Then checout::

    git clone

Create venv::

    cd caipirinha
    virtualenv-2.7 venv
    . venv/bin/activate
    python setup.py develop

Start system services::

    mongod --dbpath data &

Run web server::

    pserve development.ini

Start bot instance::

    venv/bin/caipirinha-bot development.ini

Enter IRC irc.freenode.net

Create a channel

Invite bot::

    /invite misshelp-dev #testplace

Play around.

Architecture
-------------

The service consists of

* Web UI (Pyramid + Bootstrap + MongoDB)

* Bot implementation (irclib)

Web UI and bot exchange data over MongoDB.

Initially run only one bot instance. Later scale with one bot per one process managing which IRC channel affinity.

Links
-------

* http://royal.pingdom.com/2012/04/24/irc-is-dead-long-live-irc/