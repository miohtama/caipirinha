from irc.bot import Channel

from caipirinha.bot.core import log_exceptions
from .base import CaipirinhaTestCase


class TestAuth(CaipirinhaTestCase):
    """
    Test bot joining and initial handshake.
    """

    def test_invite(self):
        """
        Check that the bot can be invited to a channel.
        """

        # Generate invite event
        # self.bot._dispatcher(None, Event("invite", 'moo-_-!miohtama@lakka.kapsi.fi', "#foobar"))

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

        self.buddy.connection.join("#foobar")
        self.wait()
        self.buddy.connection.invite("misshelp-dev", "#foobar")
        # Check that we are on the channel
        self.wait_to_happen(lambda: self.bot.hit_max_channels, "Max channels trigger not hit")

    def test_help(self):
        """
        See that you get a help messages on an unknown private command.
        """
        self.buddy.had_help = False
        self.buddy.connection.privmsg("misshelp-dev", "shiz0r")
        self.wait_for_private_notice_tag(self.buddy, "help", "Buddy got no help command explanation")

    def test_help_text(self):
        """
        See that you get a response for "help" command
        """
        self.buddy.had_help = False
        self.buddy.connection.privmsg("misshelp-dev", "help")
        self.wait_for_private_notice_tag(self.buddy, "auth", "Buddy got no long help text")

    def xxx_test_op_greet(self):
        """
        Check that we generate an auth link when op greets us.
        """
        self.buddy.connection.join("#foobar")
        self.wait()
        self.buddy.connection.invite("misshelp-dev", "#foobar")
        self.wait_to_happen(lambda: "#foobar" in self.bot.channels, "Bot never joined on invite")
        self.buddy.privmsg("misshelp-dev", "admin")


    def xxx_test_op_greet_multiple_channels(self):
        """
        Demand channel specific greet if if the same person is on multiple channels.
        """
