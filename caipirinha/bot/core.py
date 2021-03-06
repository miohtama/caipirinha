"""

    IRC bot instance.

"""
import os
import sys
import logging
import ConfigParser

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

from caipirinha.shared import get_public_url, get_database_connection
from caipirinha.log import RainbowLoggingHandler
from caipirinha.utils import get_nice_config_path
from caipirinha.utils import make_channel_spec_string
from caipirinha.bot.channelmanager import ChannelManager


def setup_logging():

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handler = RainbowLoggingHandler(sys.stdout)
    handler.show_name = False
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

setup_logging()

logger = logging.getLogger("bot")

LONG_HELP = open(os.path.join(os.path.dirname(__file__), "help.txt")).read()


def log_exceptions(func):
    """
    Decorator to log exceptinon from the resulting function.

    Because irc lib might not handle these cases in sane way.
    """

    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            logger.error(e)
            logger.exception(e)
            raise

    return inner


def get_network_from_server(server):
    """ XXX: Currently only Freenode supported
    """

    # Tests map to freenode network too
    if server in ["irc.freenode.net", "127.0.0.1", "localhost"]:
        return "freenode"

    raise RuntimeError("Cannot map server to network: %s" % server)


class ReadyAwareIRCBot(irc.bot.SingleServerIRCBot):
    """
    Let's not mess with server until we can.
    """

    def __init__(self, server, nickname, name):
        self.ready = False
        self.disconnected = False  # Used in testing
        irc.bot.SingleServerIRCBot.__init__(self, server, nickname, name)

    @log_exceptions
    def on_nomotd(self, c, e):
        """
        Server gives MOTD (or lack of it..)
        """
        self.ready = True

    @log_exceptions
    def on_motd(self, c, e):
        """
        Server gives MOTD
        """
        self.ready = True

    @log_exceptions
    def on_disconnect(self, c, e):
        """
        Server kicks you out.
        """
        self.disconnected = True

    @log_exceptions
    def on_privnotice(self, c, e):
        """
        Not used
        """
        pass


class CaiprinhaBot(ReadyAwareIRCBot):
    """
    When life gives you lemonspirit make caipirinhas.
    """

    MAX_CHANNELS = 100

    def __init__(self, config, db, channel_manager):
        """
        :param db: MongoDB handle

        :param channel_manager: Channel greet text manager instance
        """

        self.db = db
        self.config = config
        self.channel_manager = channel_manager

        self.channel_greeting_info = self.channel_manager.scan()

        self.greeting_signature = config["caipinrina.greeting_signature"]

        self.server = server = config["irc.servers"]
        port = int(config["irc.port"])
        nickname = config["irc.nick"]
        name = config["irc.name"]

        logger.info("Connecting %s" % server)
        ReadyAwareIRCBot.__init__(self, [(server, port)], nickname, name)

        self.connection.add_global_handler("welcome", self.on_welcome)

        # Expose this event for testing
        self.hit_max_channels = False

    def startup(self, c, e):
        #c.join(self.channel)
        logger.info("Connected to %s" % self.server)

        # Join all channels we have greeting message set
        network = get_network_from_server(self.server)
        channels = self.channel_manager.get_network_channels(self.channel_greeting_info, network)
        for channel in channels:
            c.join(channel)

    @log_exceptions
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    @log_exceptions
    def on_welcome(self, c, e):
        """
        :param c: Connection
        """
        self.startup(c, e)

    @log_exceptions
    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    @log_exceptions
    def on_invite(self, connection, event):
        """ Unconditionally accept all invite requets.

        Have internal limit to prevent DoSing the bot.

        :param c: irc.connection.Connection instance

        :param e: irc.client.Event instance
        """

        channel = event.arguments[0]

        if len(self.channels.keys()) >= self.MAX_CHANNELS:
            self.hit_max_channels = True
            msg = "Max channel amount reached, cannot join %s" % channel
            logger.warn(msg)
            nick = event.source.nick
            connection.notice(nick, msg)  # Tell the user to fusk off
            return

        connection.join(channel)

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

    def on_dccmsg(self, c, e):
        c.privmsg("You said: " + e.arguments[0])

    def on_join(self, c, e):
        """ When someone else joins on the channel.
        """
        self.do_greeting(c, e)

    def give_help(self, cmd, c, e):
        """
        Give a hint on unknown command.
        """
        nick = e.source.nick
        url = get_public_url(self.config)
        c.notice(nick, "Command not understood: " + cmd)
        c.notice(nick, "For help send private msg 'help'")
        c.notice(nick, "For more information visit %s" % url)

    def do_greeting(self, c, e):
        """ Output channel greeting if it has been set.
        """
        who = e.source
        channel = e.target

        # Don't greet ourselves
        nick, hostmak = who.split("!")
        if nick == c.real_nickname:
            return

        network = get_network_from_server(self.server)
        spec = make_channel_spec_string(network, channel)

        greeting = self.channel_greeting_info.get(spec)
        if greeting:
            for line in greeting.split("\n"):
                c.notice(who, line)

            c.notice(who, self.greeting_signature)

    def do_help(self, c, e):
        """ Message out for long help text version.
        """
        nick = e.source.nick
        url = get_public_url(self.config)

        help = LONG_HELP.format(self.config)

        for line in help.split("\n"):
            c.notice(nick, line)
        c.notice(nick, "For more information visit %s" % url)

    def do_admin(self, c, e, args):
        """
        Handle admin command.
        """
        nick = e.source.nick
        user_channels = []
        for name, channel in self.channels.items():
            if nick in channel.opers():
                user_channels.append(name)

        # Multiple channels confusion
        if len(user_channels) > 1 and len(args) == 0:
            c.notice(nick, "Please specify a channel from %s" % user_channels)
            return

        if len(user_channels) == 0 and len(args) == 0:
            c.notice(nick, "You must be operator on some channel")
            return

        # Read channel from the argument, or guess
        if len(args) >= 1:
            channel = args[0]
        else:
            channel = user_channels[0]

        if channel not in user_channels:
            c.notice(nick, "You must be operator on %s" % channel)
            return

        admin_link = "http://"

        c.notice(nick, "To manage %s settings go to %s" % (channel, admin_link))

    def do_command(self, e, line):
        """ Main event loop.
        """
        nick = e.source.nick
        c = self.connection

        args = line.split()
        cmd = args[0]
        args = args[1:]

        if cmd == "help":
            self.do_help(c, e)
        elif cmd == "admin":
            self.do_admin(c, e, args)
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = chobj.users()
                users.sort()
                c.notice(nick, "Users: " + ", ".join(users))
                opers = chobj.opers()
                opers.sort()
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = chobj.voiced()
                voiced.sort()
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        else:
            self.give_help(cmd, c, e)

    def execute_internal_command(msg):
        """
        """


def parse_config(file):
    """
    Read pyramid config file.
    """
    opts = {}
    config = ConfigParser.ConfigParser()
    config.read(file)

    # PasteDeploy code was a messss......
    for key in config.options("app:caipirinha"):
        opts[key] = config.get("app:caipirinha", key)

    return opts


def main():
    import sys
    if len(sys.argv) != 2:
        print "Usage: caipirinha-bot [configfile]"
        sys.exit(1)

    config_file = sys.argv[1]

    config = parse_config(config_file)

    db = get_database_connection(config)

    # Load initial greeting messages
    channel_path = get_nice_config_path(config["caipirinha.channel_data_path"])
    channel_manager = ChannelManager(get_nice_config_path(channel_path))
    channel_manager.scan()

    bot = CaiprinhaBot(config, db, channel_manager)
    logger.info("Starting")
    bot.start()

if __name__ == "__main__":
    main()
