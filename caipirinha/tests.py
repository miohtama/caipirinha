import unittest
import threading
import time

from pyramid import testing

import mongoengine

from irc.client import Event
from irc.bot import SingleServerIRCBot
from irc.bot import Channel
from irc.server import IRCServer
from irc.server import IRCClient
from caipirinha.bot.core import CaiprinhaBot
from caipirinha.mongotestcase import TestCase as MongoTestCase
from caipirinha.mongotestcase import MONGODB_TEST_DB_URL

IRC_TEST_CONF = {
    "irc.servers": "localhost",
    "irc.nick": "misshelp-dev",
    "irc.name": "Help robot Miss Caipirinha",
    "irc.port": "6667"
}


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from caipirinha.views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'caipirinha')


class ServerThread(threading.Thread):
    """
    Non-blocking IRC test server.
    """

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.server = IRCServer(("127.0.0.1", port), IRCClient)

    def run(self):
        """ """
        # Launch up a test IRC server
        self.server.serve_forever()

    def shutdown(self):
        if self.server:
            self.server.shutdown()


class BotThread(threading.Thread):
    """
    """

    def __init__(self, bot, ):
        threading.Thread.__init__(self)
        self.bot = bot

    def run(self):
        try:
            self.bot.start()
        except Exception:
            # nt.py", line 240, in process_once
            # (i, o, e) = select.select(sockets, [], [], timeout)
            # error: (9, 'Bad file descriptor')
            pass

    def disconnect(self):
        self.bot.disconnect()


class TestAuthentication(MongoTestCase):
    """
    Check that the bot can join to an ongoing channel and generate auth URLs for ops.
    """

    TEST_CASE_IRC_PORT = 6667

    def setUp(self):
        """
        """
        MongoTestCase.setUp(self)
        self.db = mongoengine.connect("testdb", host=MONGODB_TEST_DB_URL)

        TestAuthentication.TEST_CASE_IRC_PORT += 1  # Avoid socket unavailabilty error

        self.server = ServerThread(TestAuthentication.TEST_CASE_IRC_PORT)
        self.server.start()

        # An IRC user sending messages
        self.buddy = SingleServerIRCBot([("127.0.0.1", TestAuthentication.TEST_CASE_IRC_PORT)], "buddy", "Buddy'o'pal")
        self.buddy_thread = BotThread(self.buddy)
        self.buddy_thread.start()
        time.sleep(0.5)
        self.buddy = self.buddy_thread.bot

        # Our bot reacting to buddy's poking
        conf = IRC_TEST_CONF.copy()
        conf["irc.port"] = "%d" % TestAuthentication.TEST_CASE_IRC_PORT
        self.bot = CaiprinhaBot(IRC_TEST_CONF, self.db)
        self.bot_thread = BotThread(self.bot)
        self.bot_thread.start()

    def wait_until_connected(self, client):
        """
        """
        while not client.connection.is_connected():
            print "Waiting %s to connect" % client
            time.sleep(1.0)

    def tearDown(self):
        """
        Enforce shutdown for all components individually.
        """
        self.bot_thread.disconnect()

        self.buddy_thread.disconnect()

        self.server.shutdown()
        time.sleep(0.5)

    def wait(self):
        """
        Wait that server propagades all messages.
        """
        time.sleep(0.5)  # Super engineering solution

    def test_invite(self):
        """
        Check that the bot can be invited to a channel.
        """

        # Generate invite event
        # self.bot._dispatcher(None, Event("invite", 'moo-_-!miohtama@lakka.kapsi.fi', "#foobar"))

        self.wait_until_connected(self.buddy)  # Wait buddy to connect
        self.buddy.connection.join("#foobar")
        self.wait()
        self.buddy.connection.invite("misshelp-dev", "#foobar")
        self.wait()

    def test_invite_max(self):
        """
        """

        # Flood bot channels to make sure we hit the max limit
        for i in range(0, 100):
            name = "#chan%d" % i
            self.bot.channels[name] = Channel()

        self.wait_until_connected(self.buddy)  # Wait buddy to connect
        self.buddy.connection.join("#foobar")
        self.wait()
        self.buddy.connection.invite("misshelp-dev", "#foobar")
        self.wait()
