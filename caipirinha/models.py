"""

    How to store data in MongoDB.

    The structure as dumb as boot, but may serve for 0.1.

"""

import datetime
import hashlib

from mongoengine import *

# 2 days
REGREET_TIMEOUT = 2*24*60*60


class UserStatus(EmbeddedDocument):
    """ Store greeting status / per user / channel.

    We handle only joining people - people who keep connected to IRC
    are smart enough to ask smart questions.
    """

    # Identify user in IRC
    user = StringField(required=True)

    # Datetime when this user last joined the channel
    last_join = DateTimeField()

    # MongoDB can't handle intified MD5 (128bit)
    greeting_hash = StringField()

    @classmethod
    def calculate_greeting_hash(self, string):
        return hashlib.md5(string).hexdigest()

    def need_fresh_greeting(self, now):
        """ Has enough time passed that we should greet again.
        """

        if not self.last_join:
            return True

        if now - self.last_join >= datetime.timedelta(seconds=REGREET_TIMEOUT):
            return True

        return False


class ChannelStatus(Document):
    """
    Keep the state of the channel.
    """

    #: Network + channel name
    channel_spec = StringField(required=True)

    #: Hostmasks of people already joined the channel in the past. Don't greet these twice.
    known_users = ListField(field=EmbeddedDocumentField(UserStatus))

    meta = {
        'indexes': ['channel_spec']
    }

    def get_or_create_user_status(self, user):
        """
        """
        for known in self.known_users:
            if known.user == user:
                return known

        # Create new user
        user_status = UserStatus(user=user)

        self.known_users.append(user_status)
        self.save()

        return user_status

    def update_user_join_status(self, user, current_greeting, now=None):
        """ Update the status when user joins the channel.

        :param now: Supply external clock for testing

        :return: True if the user should be greeted
        """
        hash = UserStatus.calculate_greeting_hash(current_greeting)

        if not now:
            now = datetime.datetime.now()

        greet = True

        user_status = self.get_or_create_user_status(user)

        if user_status.greeting_hash != hash:
            # Msg changed
            greet = True
        else:
            if user_status.need_fresh_greeting(now):
                greet = True
            else:
                greet = False

        user_status.last_join = now
        user_status.greeting_hash = hash

        # Update the channel and this user status
        self.save()

        return greet

    @classmethod
    def get_channel(cls, channel_spec):
        """ Get or create channel spec.
        """
        channel, created = cls.objects.get_or_create(auto_save=True, channel_spec=channel_spec)
        return channel
