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
        self.wait_for_private_notice_tag(self.buddy, "Please see", "Buddy got no long help text")

    # def test_op_admin(self):
    #     """
    #     Check that we generate an auth link when op greets us.
    #     """
    #     self.buddy.connection.join("#foobar")
    #     self.wait()
    #     self.buddy.connection.invite("misshelp-dev", "#foobar")
    #     self.wait_to_happen(lambda: "#foobar" in self.bot.channels, "Bot never joined on invite")
    #     self.buddy.connection.privmsg("misshelp-dev", "admin")
    #     self.wait_for_private_notice_tag(self.buddy, "http://", "Buddy got no admin URL")

    # def test_no_op_admin(self):
    #     """
    #     Don't give admin links to no users.
    #     """
    #     self.buddy.connection.join("#foobar")
    #     self.wait()
    #     self.buddy.connection.invite("misshelp-dev", "#foobar")
    #     # http://docs.dal.net/docs/modes.html#2.13
    #     self.wait_to_happen(lambda: "#foobar" in self.bot.channels, "Bot never joined on invite")
    #     self.buddy.connection.mode("#foobar", "-o buddy")  # De-op self
    #     self.wait_to_happen(lambda: "buddy" not in self.bot.channels["#foobar"].operdict, "Buddy got not de-oped")
    #     self.wait_to_happen(lambda: "buddy" in self.bot.channels["#foobar"].userdict, "Buddy got not de-oped")

    #     # Case 1: zero op channels
    #     self.buddy.connection.privmsg("misshelp-dev", "admin")
    #     self.wait_for_private_notice_tag(self.buddy, "oper", "Buddy did not got no oper explanation")

    #     # Case 2: Specify a channel
    #     self.buddy.connection.privmsg("misshelp-dev", "admin #foobar")
    #     self.wait_for_private_notice_tag(self.buddy, "oper", "Buddy did not got no oper explanation")

    # def test_op_multiple_channels(self):
    #     """
    #     Check that we can specify the channel in the case of multiple op'ed channels.
    #     """
    #     self.buddy.connection.join("#foobar")
    #     self.buddy.connection.join("#foobar2")
    #     self.buddy.connection.invite("misshelp-dev", "#foobar")
    #     self.buddy.connection.invite("misshelp-dev", "#foobar2")
    #     self.wait_to_happen(lambda: "#foobar" in self.bot.channels, "Bot never joined on invite")
    #     self.wait_to_happen(lambda: "#foobar2" in self.bot.channels, "Bot never joined on invite")
    #     self.buddy.connection.privmsg("misshelp-dev", "admin")
    #     self.wait_for_private_notice_tag(self.buddy, "specify a channel", "Buddy got no channel explanation")
    #     self.buddy.connection.privmsg("misshelp-dev", "admin #foobar2")
    #     self.wait_for_private_notice_tag(self.buddy, "http://", "Buddy got no admin URL")

