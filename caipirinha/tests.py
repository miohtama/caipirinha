import unittest
import threading
import time
import subprocess
import os

from pyramid import testing

import mongoengine

from irc.client import Event
from irc.bot import SingleServerIRCBot
from irc.bot import Channel
from irc.server import IRCServer
from irc.server import IRCClient

import caipirinha
from caipirinha.bot.core import CaiprinhaBot
from caipirinha.mongotestcase import TestCase as MongoTestCase
from caipirinha.mongotestcase import MONGODB_TEST_DB_URL

IRC_TEST_CONF = {
    "irc.servers": "localhost",
    "irc.nick": "misshelp-dev",
    "irc.name": "Help robot Miss Caipirinha",
    "irc.port": "6667"
}

# Launch command for ngircd
NGIRCD = "/opt/local/sbin/ngircd -n -f %s"

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

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True  # Don't hung on exit
        self.running = True
        self.pid = None

    def run(self):
        """ """

        path = os.path.dirname(caipirinha.__file__)
        conf = os.path.join(path, "ngircd.conf")

        cmdline = NGIRCD % conf

        process = subprocess.Popen(cmdline.split(" "))

        while self.running:
            time.sleep(0.5)

        process.terminate()

    def shutdown(self):
        self.running = False


class BotThread(threading.Thread):
    """
    """

    def __init__(self, bot, ):
        threading.Thread.__init__(self)
        self.bot = bot
        self.daemon = True  # Don't hung on exit

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

    @classmethod
    def setUpClass(cls):
        """
        Start IRC server for running the tests
        """
        cls.server = ServerThread()
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        """
        Stop ircd.
        """
        cls.server.shutdown()

    def setUp(self):
        """
        """
        MongoTestCase.setUp(self)
        self.db = mongoengine.connect("testdb", host=MONGODB_TEST_DB_URL)

        # An IRC user sending messages to the our bot
        self.buddy = SingleServerIRCBot([("127.0.0.1", TestAuthentication.TEST_CASE_IRC_PORT)], "buddy", "Buddy'o'pal")
        self.buddy_thread = BotThread(self.buddy)
        self.buddy_thread.start()
        time.sleep(0.5)
        self.buddy = self.buddy_thread.bot

        # Our bot instance reacting to buddy's poking
        conf = IRC_TEST_CONF.copy()
        conf["irc.port"] = "%d" % TestAuthentication.TEST_CASE_IRC_PORT
        self.bot = CaiprinhaBot(IRC_TEST_CONF, self.db)
        self.bot_thread = BotThread(self.bot)
        self.bot_thread.start()

        self.wait_to_happen(lambda: self.bot.connection.is_connected(), "Bot did not connect")
        self.wait_to_happen(lambda: self.buddy.connection.is_connected(), "Buddy did not connect")

    def wait_until_connected(self, bot):
        """
        """
        while not bot.connection.is_connected():
            print "Waiting %s to connect" % bot._nickname
            time.sleep(1.0)

    def tearDown(self):
        """
        Enforce shutdown for all components individually.
        """
        self.bot_thread.disconnect()

        self.buddy_thread.disconnect()

    def wait(self):
        """
        Wait that server propagades all messages.
        """
        time.sleep(0.5)  # Super engineering solution

    def wait_to_happen(self, func, msg):
        """
        """
        tick = 0.1
        still_waiting = 5.0
        while not func():
            time.sleep(tick)
            still_waiting -= tick
            if still_waiting < 0:
                raise AssertionError(msg)

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
        # Check that we are on the channel
        self.wait_to_happen(lambda: "#foobar" in self.bot.channels, "Bot never joined on invite")

    def test_invite_max_channels_reached(self):
        """
        Don't join the channel if we hit the channel count ceiling
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
        self.assertTrue(self.bot.hit_max_channels)
