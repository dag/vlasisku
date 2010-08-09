#!/usr/bin/env python
#-*- coding:utf-8 -*-

from flaskext.script import Manager

from vlasisku import app


manager = Manager(app)


@manager.command
def runbots():
    """Start the IRC bots valsi and gerna."""

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    from vlasisku.irc import GrammarBotFactory, WordBotFactory

    gerna = GrammarBotFactory()
    valsi = WordBotFactory()

    log.startLogging(sys.stdout)
    reactor.connectTCP(gerna.server, gerna.port, gerna)
    reactor.connectTCP(valsi.server, valsi.port, valsi)
    reactor.run()


@manager.shell
def shell_context():

    import pprint

    import flask

    import vlasisku

    context = dict(pprint=pprint.pprint)
    context.update(vars(flask))
    context.update(vars(vlasisku))
    context.update(vars(vlasisku.utils))
    context.update(vars(vlasisku.database))
    context.update(vars(vlasisku.models))

    return context


if __name__ == "__main__":
    manager.run()
