from __future__ import with_statement
from fabric.api import *

env.hosts = ['lojban.org']
appdir = '/home/dag/vlasisku'
virtenv = '/home/dag/.virtualenvs/vlasisku'


def restart():
    run('touch %s/app.wsgi' % appdir)

def retag():
    with cd(appdir):
        run('rm data/db.pickle')
        run('touch data/jbovlaste.xml')
    restart()

def syncdb():
    with cd(appdir):
        run('wget "http://jbovlaste.lojban.org/export/xml-export.html?lang=en" -O data/jbovlaste.xml')
    retag()

def pull():
    with cd(appdir):
        run('bzr pull')

def installdeps():
    with cd(appdir):
        run('pip install -E %s -r requirements.txt' % virtenv)

def updatedeps():
    with cd(appdir):
        run('pip install -E %s -r requirements.txt -u' % virtenv)

def deploy():
    local('bzr push')
    pull()
    installdeps()
    restart()

