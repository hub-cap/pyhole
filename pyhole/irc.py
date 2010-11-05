"""
IRC Class 
"""


import irclib
import time


class IRC(irclib.SimpleIRCClient):
    """IRC Class"""
    def __init__(self, config, logger):
        """Initiate IRC connection

        Args:
            config
            logger
        """
        irclib.SimpleIRCClient.__init__(self)

        self.log = logger
        self.config = config

        self.server = config.get("server")
        self.port = config.get("port", "int")
        self.nick = config.get("nick")
        self.channel = config.get("channel")
        self.command_prefix = config.get("command_prefix")

        self.log.info("Connecting to %s:%d as %s" % (
            self.server,
            self.port,
            self.nick)
        )
        self.connect(self.server, self.port, self.nick)

    def on_nicknameinuse(self, connection, event):
        """Ensure the use of unique IRC nick

        Args:
            connection
            event
        """
        self.log.info("IRC nick '%s' is currently in use" % self.nick)
        connection.nick("_%s_" % self.nick)
        self.log.info("Setting IRC nick to '_%s_'" % self.nick)

    def on_welcome(self, connection, event):
        """Join channel upon successful connection

        Args:
            connection
            event
        """
        if irclib.is_channel(self.channel):
            self.log.info("Joining %s" % self.channel)
            connection.join(self.channel)

    def on_disconnect(self, connection, event):
        """Attempt to reconnect after disconnection

        Args:
            connection
            event
        """
        self.log.info("Disconnected from %s:%d" % (self.server, self.port))
        time.sleep(15)
        self.log.info("Attempting to reconnect in 15 seconds")
        self.connect(self.server, self.port, self.nick)

    def on_privmsg(self, connection, event):
        """Handle private messages

        Args:
            connection
            event
        """
        nick = event.source().split("!")[0]
        msg = event.arguments()[0]

        if nick != self.nick:
            self.log.info("<%s> %s" % (nick, msg))
            #connection.privmsg(nick, "[%s] %s" % (nick, msg))

    def on_pubmsg(self, connection, event):
        """Handle public messages

        Args:
            connection
            event
        """
        target = event.target()
        nick = event.source().split("!")[0]
        msg = event.arguments()[0]

        if target == self.channel:
            self.log.info("%s <%s> %s" % (target, nick, msg))
            if msg == self.command_prefix + "foo":
                connection.privmsg(target, "bar")
