import threading
import time
import subprocess
import os

import mongoengine

import caipirinha
from caipirinha.bot.core import ReadyAwareIRCBot
from caipirinha.bot.core import CaiprinhaBot
from caipirinha.mongotestcase import TestCase as MongoTestCase
from caipirinha.mongotestcase import MONGODB_TEST_DB_URL

IRC_TEST_CONF = {
    "irc.servers": "localhost",
    "irc.nick": "misshelp-dev",
    "irc.name": "Help robot Miss Caipirinha",
    "irc.port": "6667",
    "caipirinha.public_url": "http://www.misshelp.org"
}

# Launch command for ngircd
NGIRCD = "/opt/local/sbin/ngircd -n -f %s"


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
        MongoTestCase.setUp(self)
        self.db = mongoengine.connect("testdb", host=MONGODB_TEST_DB_URL)

        # An IRC user sending messages to the our bot
        self.buddy = ReadyAwareIRCBot([("127.0.0.1", CaipirinhaTestCase.TEST_CASE_IRC_PORT)], "buddy", "Buddy'o'pal")
        self.buddy_thread = BotThread(self.buddy)
        self.buddy_thread.start()
        time.sleep(0.5)
        self.buddy = self.buddy_thread.bot

        # Our bot instance reacting to buddy's poking
        conf = IRC_TEST_CONF.copy()
        conf["irc.port"] = "%d" % CaipirinhaTestCase.TEST_CASE_IRC_PORT
        self.bot = CaiprinhaBot(IRC_TEST_CONF, self.db)
        self.bot_thread = BotThread(self.bot)
        self.bot_thread.start()

        self.wait_to_happen(lambda: self.bot.ready, "Bot did not connect")
        self.wait_to_happen(lambda: self.buddy.ready, "Buddy did not connect")

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
        Async assertation which waits a certain timeout before bailing out.
        """
        tick = 0.1
        still_waiting = 5
        while not func():
            time.sleep(tick)
            still_waiting -= tick
            if still_waiting < 0:
                raise AssertionError(msg)


