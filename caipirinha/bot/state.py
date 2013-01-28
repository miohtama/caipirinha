"""

    Classes to maintain IRC bot internal state and communicate with external systems.

"""


class NetworkManager(object):
    """
    Handle state of one IRC network.
    """

    def __init__(self, network, db):
        self.network = network
        self.db = db
        self.channels = {}  # Channel name -> ChanneManager instance

    def handle_private_message(self, msg):
        """
        """

    def on_invite(self, source, arguments, bot):
        """ Handle channel invites the bot receives.

        Always join when invited.

        :param source: String like 'moo-_-!miohtama@lakka.kapsi.fi'

        :param arguments: Python list of IRC command arguments

        :param bot: irc.client.Client instance or similar mock-up
        """
        bot.join(arguments[0])  # Channel

    def on_after_join(self, name, channel, bot):
        """
        :param channel: irc.bot.Channel instance
        """
        self.channels[name] = ChannelManager(channel)

    def find_channels_by_user(self):
        """
        Search all channels where the user is.

        :return: List of channel names
        """


class ChannelManager(object):
    """
    Maintain the state of the channel.

    Provide mocking interface for unit tests.
    """

    STATE_FRESH = "fresh"

    STATE_STABLE = "stable"

    def __init__(self, channel):
        """
        :param channel: irc.bot.Channel instance
        """
        self.channel = channel

