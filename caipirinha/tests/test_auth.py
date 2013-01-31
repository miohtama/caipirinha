from irc.bot import Channel

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