"""

    MIsc shiz0r.

"""


import os


def make_channel_spec_string(network, channel):
    """
    """

    assert network is not None
    assert channel is not None

    return "{network}!{channel}".format(**locals())


def split_channel_spec(spec):
    """
    """
    return spec.split("!")


def get_nice_config_path(path):
    """ Make sure a path read from the config is absolute or relative to the current working dir.
    """
    if path.startswith("/"):  # No windows
        return path
    return os.path.join(os.gecwd(), path)

