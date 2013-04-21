"""

    Data models to describe our world.

    Channel spec is in format

        irc://irc.freenode.net/#channel

"""

from mongoengine import *


class Authorization(Document):
    """
    IRC channel operators authorizes access to a channel configuration.
    """

    #: User nick who requested this
    nick = StringField(required=True)

    #: User full hostmask
    mask = StringField(required=True)

    #: Network + channel name
    channel_spec = StringField(required=True)

    #: Authorization link token
    auth_magic = StringField(required=True, unique=True)

    #: When authorization was created - checked for validy
    created = DateTimeField(required=True)

    meta = {
        'indexes': ['channel_spec']
    }


class Trigger(EmbeddedDocument):
    """
    Bot scans for a channel messages and executes trigger.executes
    """

    # !hello etc. style triggers
    SCANNING_EXCLAMANATION = "!"

    # How trigger detects action
    scanning_type = StringField(required=True)

    scanning_keyword = StringField(required=True)

    # Use URL callback to get the answer
    url = StringField()

    # Post predefined text
    text = StringField()


class ChannelConfiguration(Document):
    """
    Description
    """

    #: Full functional
    MODE_ACTIVE = "active"

    #: Stay on channel, don't greet, collect logs
    MODE_QUIET = "active"

    #: Leave the channel
    MODE_PARTS = "parts"

    GREETING_DEFAULT = "default"

    GREETINGS_DEFAULT_AND_CUSTOM = "defaut+custom"

    GREETINGS_CUSTOM = "custom"

    #: Network + channel name
    channel_spec = StringField(required=True)

    #: One of mode constants
    mode = StringField(required=True)

    project_name = StringField(required=True)

    project_url = URLField(required=False)

    howto_mode = StringField(required=True)

    #: What to say when joining to channel
    howto_text = StringField(required=False)

    #: Alternative forums where to ask help
    alternatives_text = StringField(required=False)

    #: Allow reading / searching backlogs from web
    public_log = BooleanField(required=False)

    #: Custom channel triggers
    triggers = ListField(EmbeddedDocumentField(Trigger))

    meta = {
        'indexes': ['channel_spec']
    }


class ChannelStatus(Document):
    """
    Keep the state of the channel.
    """

    #: Network + channel name
    channel_spec = StringField(required=True)

    #: Hostmasks of people already joined the channel in the past. Don't greet these twice.
    known_people = ListField(StringField())


class Homepage(EmbeddedDocument):
    """
    Channel homepage information.

    EXtra informatino available in web status page besides of those in ChannelConfiguration.
    """

    intro_text = StringField(required=False)


class ChannelLogstats(Document):
    """
    Contains channel statistics + logs for one day.

    We also have statistic fields which are updated run-time / postprocessed when the day is complete.
    """

    channel_spec = StringField(required=True)

    date = DateTimeField(required=False)

    min_users = IntField(required=False)

    max_users = IntField(required=False)

    #: Store channel logs, one string per message
    log = ListField(field=StringField)
