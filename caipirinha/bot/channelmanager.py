""" Manager channel greet message specifications.

"""

import os
import logging

from caipirinha.utils import make_channel_spec_string

logger = logging.getLogger("caipirinha.channelmannager")


class ChannelManager(object):
    """ Read channel greeting text files from a static folder.
    """

    def __init__(self, folder):
        """ Initialize channel manager on a certain folder.

        :param: folder Absolute path where channel specification files are
        """
        self.folder = folder

        #: Map of (network, channel) -> Greetingtext tuples
        self.channels = {}

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

    def get_channels(self):
        """ Return mappings (mutable copy)
        """
        return self.channels.copy()

    def scan(self):
        """ Toggle channel data rescan.
        """

        files = os.listdir(self.folder)

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
            self.channels[key] = content



