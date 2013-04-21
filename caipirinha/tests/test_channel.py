import os
import unittest
import sys

from irc.bot import Channel
from caipirinha.bot.channelmanager import ChannelManager
from caipirinha.utils import make_channel_spec_string

from .base import CaipirinhaTestCase

TEST_CHANNELS_PATH = os.path.join(os.path.dirname(sys.modules[__name__].__file__), "channel-test-data")


class TestChannelManager(unittest.TestCase):
    """ See that we discover channel files ok.
    """

    def setUp(self):
        self.manager = ChannelManager(TEST_CHANNELS_PATH)

    def test_spec_string(self):
        """ Spec string is what it should be
        """
        self.assertEqual("irc://freenode/#caipirinha", make_channel_spec_string("freenode", "#caipirinha"))

    def test_scan(self):
        """ We scan data files correctly """
        self.manager.scan()
        # We have two valid channels in test data
        self.assertEqual(2, len(self.manager.get_channels().keys()))

        channels = self.manager.get_channels()
        self.assertTrue(make_channel_spec_string("freenode", "#caipirinha-test") in channels)
        self.assertTrue(make_channel_spec_string("freenode", "#caipirinha.test2") in channels)


class TestChannelGreet(CaipirinhaTestCase):
    """ Test that we behave on channels.
    """

    def test_get_channel_url(self):
        """
        Check that we can specify the channel in the case of multiple op'ed channels.
        """
