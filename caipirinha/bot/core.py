"""

    IRC bot instance.

"""
import sys
import logging
import ConfigParser

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr


def setup_logging():

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

setup_logging()

logger = logging.getLogger("bot")


class CaiprinhaBot(irc.bot.SingleServerIRCBot):
    """
    When life gives you lemonspirit make caipirinhas.
    """

    MAX_CHANNELS = 100

    def __init__(self, config, db):

        self.db = db

        self.server = server = config["irc.servers"]
        port = int(config["irc.port"])
        nickname = config["irc.nick"]
        name = config["irc.name"]
        logger.info("Connecting %s" % server)

        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, name)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        #c.join(self.channel)
        logger.info("Connected to %s" % self.server)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_invite(self, connection, event):
        """ Unconditionally accept all invite requets.

        XXX: Set a max limit of chhanels

        :param c: ?

        :param e: irc.client.Event instance
        """

        channel = event.target

        if len(self.channels.keys()) > self.MAX_CHANNELS:
            msg = "Max channel amount reached, cannot join %s" % channel
            logger.warn(msg)
            nick = event.source.nick
            connection.notice(nick, msg)  # Tell the user to fusk off
            return

        connection.join(event.target)

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

    def on_dccmsg(self, c, e):
        c.privmsg("You said: " + e.arguments[0])

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
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
            c.notice(nick, "Not understood: " + cmd)

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

    bot = CaiprinhaBot(config, db)
    logger.info("Starting")
    bot.start()

if __name__ == "__main__":
    main()
