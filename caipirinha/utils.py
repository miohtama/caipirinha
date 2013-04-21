"""

    MIsc shiz0r.

"""


def make_channel_spec_string(network, channel):
    """
    """

    assert network is not None
    assert channel is not None

    return "irc://{network}/{channel}".format(**locals())
