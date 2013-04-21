import threading
import time
import subprocess
import os
import logging
import sys

import mongoengine

import caipirinha
from caipirinha.bot.core import ReadyAwareIRCBot
from caipirinha.bot.core import CaiprinhaBot
from caipirinha.bot.core import log_exceptions
from caipirinha.bot.channelmanager import ChannelManager

from caipirinha.mongotestcase import TestCase as MongoTestCase
from caipirinha.mongotestcase import MONGODB_TEST_DB_URL

logger = logging.getLogger("test")

IRC_TEST_CONF = {
    "irc.servers": "localhost",
    "irc.nick": "misshelp-dev",
    "irc.name": "Help robot Miss Caipirinha",
    "irc.port": "6667",
    "caipirinha.public_url": "http://www.misshelp.org",
    "caipirinha.channel_data_path": "caipirinha/tests/channel-test-data",
    "caipinrina.greeting_signature": "For more information visit example.com"
}

# Launch command for ngircd
NGIRCD = "/opt/local/sbin/ngircd -n -f %s"

TEST_CHANNELS_PATH = os.path.join(os.path.dirname(sys.modules[__name__].__file__), "channel-test-data")


class ServerThread(threading.Thread):
    """
    Non-blocking IRC test server.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = False  # Don't hung on exit
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

nick_counter = 0


class CaipirinhaTestCase(MongoTestCase):
    """
    Check that the bot can join to an ongoing channel and generate auth URLs for ops.
    """

    TEST_CASE_IRC_PORT = 6667

    @classmethod
    def setUpClass(cls):
        """
        Start IRC server for running the tests
        """
        os.system("killall ngircd")
        cls.server = ServerThread()
        cls.server.start()
        time.sleep(1.5)  # Let server wake up

    @classmethod
    def tearDownClass(cls):
        """
        Stop ircd.
        """
        cls.server.shutdown()

    def setUp(self):
        """
        """

        global nick_counter

        MongoTestCase.setUp(self)
        self.db = mongoengine.connect("testdb", host=MONGODB_TEST_DB_URL)

        # An IRC user sending messages to the our bot

        # Workaround to avoid nick already in use exceptions
        nick = "buddy%d" % nick_counter
        nick_counter += 1
        self.buddy = ReadyAwareIRCBot([("127.0.0.1", CaipirinhaTestCase.TEST_CASE_IRC_PORT)], nick, "Buddy'o'pal")
        self.buddy_thread = BotThread(self.buddy)
        self.buddy_thread.start()
        time.sleep(0.5)
        self.buddy = self.buddy_thread.bot

        # Our bot instance reacting to buddy's poking
        conf = IRC_TEST_CONF.copy()
        conf["irc.port"] = "%d" % CaipirinhaTestCase.TEST_CASE_IRC_PORT
        self.bot = CaiprinhaBot(IRC_TEST_CONF, self.db, ChannelManager(TEST_CHANNELS_PATH))
        self.bot_thread = BotThread(self.bot)
        self.bot_thread.start()

        self.wait_to_happen(lambda: self.bot.ready, "Bot did not connect")

        logger.info("Waiting buddy to connect")
        self.wait_to_happen(lambda: self.buddy.ready, "Buddy did not connect")
        logger.info("Buddy connected")

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

        # We need to wait to avoid nickname in use errors
        if self.bot.ready:
            self.wait_to_happen(lambda: self.bot.disconnected, "Bot did not disconnect")

        if self.buddy.ready:
            self.wait_to_happen(lambda: self.buddy.disconnected, "Buddy did not dicconnect")

    def join_to_channel(self, client, channel):
        """ Make simulated user to join an IRC channel.

        Synchronous. Return when the IRC client channel state is complete for the channel.
        """
        client.connection.join(channel)
        self.wait()  # XXX: Wait here for the channel initialization, not random time

    def wait(self):
        """
        Wait that server propagades all messages.
        """
        time.sleep(0.5)  # Super engineering solution

    def wait_to_happen(self, func, msg):
        """
        Async assertation which waits a certain timeout before bailing out.
        """

        tick = 0.1
        still_waiting = 10
        while not func():
            time.sleep(tick)
            still_waiting -= tick
            if still_waiting < 0:
                raise AssertionError(msg)

    def wait_for_private_notice_tag(self, bot, tag, msg):
        """
        Wait to see if we get a notification of tag in the private notices.
        """

        bot.had_it = False

        @log_exceptions
        def got_it(c, e):
            """ privmsg mock """
            if tag in e.arguments[0]:
                bot.had_it = True

        bot.on_privnotice = got_it
        self.wait_to_happen(lambda: bot.had_it, msg)
