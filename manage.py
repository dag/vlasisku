#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import with_statement

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


@manager.command
def updatedb():
    """Export and index a new database from jbovlaste."""

    from contextlib import closing
    from urllib2 import urlopen
    import xml.etree.cElementTree as etree
    import os

    url = 'http://jbovlaste.lojban.org/export/xml-export.html?lang=en'
    with closing(urlopen(url)) as data:
        xml = etree.parse(data)
        assert xml.getroot().tag == 'dictionary'
        with open('vlasisku/data/jbovlaste.xml', 'w') as file:
            xml.write(file, 'utf-8')
        os.system('''
            rm -f vlasisku/data/db.pickle
            touch app.wsgi
            ''')


if __name__ == "__main__":
    manager.run()
