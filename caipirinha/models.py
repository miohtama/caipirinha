"""

    Data models to describe our world.

    Channel spec is in format

        irc://irc.freenode.net/#channel

"""

from mongoengine import *


class ChannelStatus(Document):
    """
    Keep the state of the channel.
    """

    #: Network + channel name
    channel_spec = StringField(required=True)

    #: Hostmasks of people already joined the channel in the past. Don't greet these twice.
    known_people = ListField(StringField())


