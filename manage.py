#!/usr/bin/env python

from werkzeug import script


def make_app():
    from vlasisku import app
    return app


def make_shell():
    from vlasisku import app, db, render
    from utils import compound2affixes, tex2html, \
                      braces2links, dameraulevenshtein
    from db import DB
    from models import Entry, Gloss
    return locals()


action_runserver = script.make_runserver(make_app, use_reloader=True,
                                                   use_debugger=True,
                                                   hostname='127.0.0.1')
action_shell = script.make_shell(make_shell)


if __name__ == '__main__':
    script.run()

