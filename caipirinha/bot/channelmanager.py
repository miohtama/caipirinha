""" Manager channel greet message specifications.

"""

import os
import logging

from caipirinha.utils import make_channel_spec_string
from caipirinha.utils import split_channel_spec

logger = logging.getLogger("caipirinha.channelmannager")


class ChannelManager(object):
    """ Read channel greeting text files from a static folder.
    """

    def __init__(self, folder):
        """ Initialize channel manager on a certain folder.

        :param: folder Absolute path where channel specification files are
        """
        self.folder = folder

    def get_channel_spec(self, f):
        """ Extract channel network + name

        :param f: File

        :return: (None, None) if not a channel file or (network, channel)
        """

        if not f.startswith("#"):
            return (None, None)

        if not f.endswith(".txt"):
            return (None, None)

        parts = f.split(".")

        # name + network + txt
        if len(parts) < 3:
            return (None, None)

        name = ".".join(parts[:-2])
        network = parts[-2]

        return (network, name)

    def scan(self):
        """ Toggle channel data rescan.

        :return: Dict of scanned greet messages
        """

        files = os.listdir(self.folder)

        channels = {}

        if len(files) == 0:
            raise RuntimeError("No channel data in folder %s" % self.folder)

        for f in files:

            network, name = self.get_channel_spec(f)
            if not name:
                # Not a channel file
                continue

            try:
                stream = open(os.path.join(self.folder, f), "rt")
                content = stream.read().decode("utf-8")
                stream.close()
            except Exception as e:
                logger.error("Could not read channel %s" % f)
                logger.exception(e)

            key = make_channel_spec_string(network, name)
            channels[key] = content

        return channels

    def reload(self, new_channels, old_channels, add_callback, delete_callback):
        """ Instiate new channel data.
        """

        # See which channels disappear
        for spec in old_channels.keys():
            if not spec in new_channels:
                delete_callback(spec)
                del old_channels[spec]

        # See which are new channels
        for spec in new_channels.keys():
            if not spec in new_channels:
                delete_callback(spec)

    def get_network_channels(self, channels, network):
        """ Get list of a channels of certain network.
        """
        for spec in channels.keys():
            network, channel = split_channel_spec(spec)
            if network == network:
                yield channel

