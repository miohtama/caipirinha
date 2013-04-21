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

        # We have two valid channels in test data
        channels = self.manager.scan()
        self.assertEqual(2, len(channels.keys()))

        self.assertTrue(make_channel_spec_string("freenode", "#caipirinha-test") in channels)
        self.assertTrue(make_channel_spec_string("freenode", "#caipirinha.test2") in channels)

    def test_rescan(self):
        """ See that we fire events for add end delete channels.
        """

        existing_channel = make_channel_spec_string("freenode", "#caipirinha-test")
        deleted_channel = make_channel_spec_string("freenode", "#caipirinha.test2")
        added_channel = make_channel_spec_string("freenode", "#caipirinha.test.3")

        old_data = self.manager.scan()
        new_data = {
            existing_channel: "",
            added_channel: ""
        }

        def added(channel):
            self.assertEqual(channel, added_channel)

        def deleted(channel):
            self.assertEqual(channel, deleted_channel)

        self.manager.reload(new_data, old_data, added, deleted)


class TestChannelGreet(CaipirinhaTestCase):
    """ Test that we behave on channels.
    """

    def test_get_greet_message(self):
        """
        Check that we can specify the channel in the case of multiple op'ed channels.
        """

        self.join_to_channel(self.bot, "#caipirinha-test")

        self.buddy.connection.join("#caipirinha-test")
        self.wait_for_private_notice_tag(self.buddy, "Caipirinha channel greet example message.", "Buddy got no greeting message")

    def test_do_not_get_greet_messge_twice(self):
        """
        """

    def test_do_greet_message_again_after_timeout(self):
        """
        """

