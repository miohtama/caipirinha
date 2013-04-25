Miss Caipirinha is an IRC help bot provided as a hosted service. It is designed to be an infrastructure tool for open source communities to make community support discussion (help chat in IRC) more streamlined by
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

Installation
+++++++++++++++

    sudo port install mongdodb

Then checout::

    git clone

Create venv::

    cd caipirinha
    virtualenv-2.7 venv
    . venv/bin/activate
    python setup.py develop

Running
++++++++

*Note*: There is *Makefile* which contains example commands how to run this thing

Start MongoDB services::

    mongod --dbpath data &

Start server::

    /opt/local/sbin/ngircd -n -f caipirinha/ngircd.conf &

Start bot instance::

    venv/bin/caipirinha-bot development.ini

Run irssi in another terminal::

    irssi
    /connect localhost
    /join #caipirinha-test

Play around.

Using Makefile
++++++++++++++++

In terminal A to start IRC and bot::

    make start-development-bot

In terminal B to start a test user:

    make irssi

Unit tests
-------------

Unit tests need a local functional IRC server.

Install ngircd, needed to run tests::

    sudo port install ngircd

Run one test::

    python -m unittest caipirinha.tests

Run all tests::

    python -m unittest discover

Architecture
-------------

The service consists of

* Questions.io website built using a static site generator `Pelican <http://docs.getpelican.com/>`_, hosted on Github

* Channel greeting messages are managed through Github web inline edit interface through Github forks

* UNIX cron scripts notifies the bot when the channel messages change

* The bot is implemented using Python, irclib and it keeps its state in MongoDB

Initially run only one bot instance. Later scale with one bot per one process managing which IRC channel affinity.

Links
-------

* http://royal.pingdom.com/2012/04/24/irc-is-dead-long-live-irc/

* http://martinbrochhaus.com/2012/02/pelican.html

* `Pelican theme inspiration <https://github.com/getpelican/pelican-themes/tree/master/bootstrap2/templates>`_

Author
--------------

Mikko Ohtamaa (`blog <https://opensourcehacker.com>`_, `Facebook <https://www.facebook.com/?q=#/pages/Open-Source-Hacker/181710458567630>`_, `Twitter <https://twitter.com/moo9000>`_, `Google+ <https://plus.google.com/u/0/103323677227728078543/>`_)



