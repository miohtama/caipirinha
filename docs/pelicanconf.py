#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u'Mikko Ohtamaa'
SITENAME = u'GoodQuestion.io'
SITEURL = ''

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'

# Blogroll
LINKS = (('Pelican', 'http://docs.notmyidea.org/alexis/pelican/'),
        ('Python.org', 'http://python.org'),
        ('Jinja2', 'http://jinja.pocoo.org'),
        ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

THEME = "theme"

DISPLAY_PAGES_ON_MENU = True

# custom page generated with a jinja2 template
TEMPLATE_PAGES = {'pages/irc.html': 'pages/irc.html'
}

STASTIC_PATHS = ["static"]
