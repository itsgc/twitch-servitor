#!/usr/bin/env python2

"""A really simple IRC bot."""

import sys
from twisted.internet import reactor, protocol
from twisted.words.protocols import irc
from yaml import load

class Bot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)
    with open('creds.yml', 'r') as credsfile:
        creds = load(credsfile)
        twitch_token = creds['twitch_irc_token']

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % self.nickname

    def joined(self, channel):
        print "Joined %s." % channel

    def privmsg(self, user, channel, msg):
        print msg

class BotFactory(protocol.ClientFactory):
    protocol = Bot

    def __init__(self, channel, nickname='twitch-servitor'):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Connection lost. Reason: %s" % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
       print "Connection failed. Reason: %s" % reason

if __name__ == "__main__":
    chan = "#karmik-twitchtest"
    reactor.connectTCP('irc.freenode.net', 6667, BotFactory(chan))
    reactor.run()