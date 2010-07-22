#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

from twisted.python import log
from twisted.internet import reactor

from vlasisku.irc import GrammarBotFactory


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    factory = GrammarBotFactory()
    reactor.connectTCP(factory.server, factory.port, factory)
    reactor.run()

