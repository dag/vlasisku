#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

from twisted.python import log
from twisted.internet import reactor

from vlasisku.irc import WordBotFactory


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    factory = WordBotFactory()
    reactor.connectTCP(factory.server, factory.port, factory)
    reactor.run()

