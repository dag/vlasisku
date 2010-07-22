#-*- coding:utf-8 -*-

import re

from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log
from twisted.words.protocols.irc import IRCClient

from vlasisku import db
from vlasisku.utils import strip_html, jbofihe


class BotBase(IRCClient):

    def signedOn(self):
        log.msg('* Logged on')
        self.factory.resetDelay()
        self.join(self.factory.channels)

    # The inherited implementation passes notices to privmsg, causing upset.
    def noticed(self, user, channel, message):
        pass

    def msg(self, target, message):
        log.msg('<%(nickname)s> %(message)s' %
            dict(nickname=self.nickname, message=message))
        IRCClient.msg(self, target, message)

    def privmsg(self, user, channel, message):
        nick = user[:user.index('!')]

        # PM?
        if channel == self.nickname:
            target = nick
        else:
            target = channel

        query = None
        if target != channel:
            query = message
        else:
            trigger = r'^%(nickname)s[:,]? (?P<query>.+)' \
                    % dict(nickname=re.escape(self.nickname))
            match = re.match(trigger, message)
            if match:
                query = match.group('query')

        if query:
            log.msg('<%(nick)s> %(message)s' % locals())
            self.query(target, query)

class FactoryBase(ReconnectingClientFactory):
    server = 'irc.freenode.net'
    port = 6667
    channels = '#lojban,#jbopre,#vlaski'


class WordBot(BotBase):

    nickname = 'valsi'

    def query(self, target, entry):
        url = 'http://vlasisku.lojban.org/%s' % entry.replace(' ', '+')
        if entry in db.entries:
            format = '%(entry)s = %(definition)s'
            definition = strip_html(db.entries[entry]
                                   .definition.encode('utf-8'))
        else:
            format = u'%(entry)s ≠ defined. %(url)s'.encode('utf-8')
        self.msg(target, format % locals())

class WordBotFactory(FactoryBase):
    protocol = WordBot


class GrammarBot(BotBase):

    nickname = 'gerna'

    def query(self, target, query):
        try:
            response = jbofihe(query)
        except ValueError, e:
            response = e

        self.msg(target, response)

class GrammarBotFactory(FactoryBase):
    protocol = GrammarBot

