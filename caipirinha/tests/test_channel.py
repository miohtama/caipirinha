from irc.bot import Channel

from .base import CaipirinhaTestCase


class TestChannelGreet(CaipirinhaTestCase):
    """
    Test that we behave on channels.
    """

    def test_get_channel_url(self):
        """
        Check that we can specify the channel in the case of multiple op'ed channels.
        """
