
from __future__ import with_statement

from fabric.api import *


env.hosts = ['lojban.org']
appdir = '/home/dag/vlasisku'
virtenv = '/home/dag/.virtualenvs/vlasisku'


def restart():
    run('touch %s/app.wsgi' % appdir)

def retag():
    with cd(appdir):
        run('touch vlasisku/data/db.pickle')
        run('touch vlasisku/data/jbovlaste.xml')
    restart()

def redb():
    with cd(appdir):
        run('rm vlasisku/data/db.pickle')
    retag()

def syncdb():
    with cd(appdir):
        run('rm vlasisku/data/db.pickle')
        run('wget "http://jbovlaste.lojban.org/export/xml-export.html?lang=en"'
            ' -O vlasisku/data/jbovlaste.xml')
    restart()

def pull():
    with cd(appdir):
        run('bzr pull')

def installdeps():
    with cd(appdir):
        run('pip install -E %s -r requirements.txt' % virtenv)

def updatedeps():
    with cd(appdir):
        run('pip install -E %s -r requirements.txt -U' % virtenv)

def deploy():
    local('bzr push')
    pull()
    installdeps()
    restart()

def startbots():
    with cd(appdir):
        run("""
            source %s/bin/activate
            nohup ./manage.py runbots >/dev/null &
        """ % virtenv)
