from irc.bot import Channel

from .base import CaipirinhaTestCase


class TestChannelSettings(CaipirinhaTestCase):
    """
    Test setting channel settings throught the web interface.
    """

    def test_get_channel_url(self):
        """
        Check that we can specify the channel in the case of multiple op'ed channels.
        """
