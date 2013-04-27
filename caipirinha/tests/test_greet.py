"""

    Test greeting logic.

"""


import datetime

from .base import CaipirinhaMongoTestCase

from models import ChannelStatus, REGREET_TIMEOUT
from utils import make_channel_spec_string


class TestGreeting(CaipirinhaMongoTestCase):
    """
    Test bot joining and initial handshake.
    """

    def setUp(self):
        super(TestGreeting, self).setUp()
        self.user = "Moo-_-!miohtama@lakka.kapsi.fi"
        self.greeting = "Foobar"
        self.channel = make_channel_spec_string("freenode", "#goodquestion")

    def test_fresh(self):
        """ Test that we get greeting when we join for the first time.
        """

        channel = ChannelStatus.get_channel(channel_spec=self.channel)
        greet = channel.update_user_join_status(self.user, self.greeting)
        self.assertEqual(True, greet)

    def test_double_join(self):
        """ Same user joins twice too fast """
        now = datetime.datetime.now()

        channel = ChannelStatus.get_channel(channel_spec=self.channel)
        greet = channel.update_user_join_status(self.user, self.greeting, now=now)
        now += datetime.timedelta(seconds=0.1)

        greet = channel.update_user_join_status(self.user, self.greeting, now=now)
        self.assertEqual(False, greet)

    def test_timeout(self):
        """ User joins twice in long period """
        now = datetime.datetime.now()
        channel = ChannelStatus.get_channel(channel_spec=self.channel)
        greet = channel.update_user_join_status(self.user, self.greeting, now=now)
        now += datetime.timedelta(seconds=REGREET_TIMEOUT) + datetime.timedelta(seconds=100)

        greet = channel.update_user_join_status(self.user, self.greeting, now=now)
        self.assertEqual(True, greet)
