#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import with_statement

from bottle import route, view, response, request, abort, send_file, redirect
from utils import etag
import db
from os.path import join, dirname
from utils import ignore
from simplejson import dumps
import re


@route('/')
@view('index')
@etag(db.etag)
def index():
    types = (('gismu', 'Root words.'),
             ('cmavo', 'Particles.'),
             ('cmavo cluster', 'Particle combinations.'),
             ('lujvo', 'Compound words.'),
             ("fu'ivla", 'Loan words.'),
             ('experimental gismu', 'Non-standard root words.'),
             ('experimental cmavo', 'Non-standard particles.'),
             ('cmene', 'Names.'))
    classes = set(e.grammarclass for e in db.entries.itervalues()
                                 if e.grammarclass)
    scales = db.class_scales
    return locals()


@route('/(?P<filename>favicon\.ico)')
@route('/static/:filename#.+#')
def static(filename):
    send_file(filename, root=join(dirname(__file__), 'static'))


@route('/opensearch')
@view('opensearch')
def opensearch():
    response.content_type = 'application/xml'
    return dict(hostname=request.environ['HTTP_HOST'])

@route('/suggest/:prefix')
def suggest(prefix):
    suggestions = []
    types = []
    entries = (e for e in db.entries.iterkeys()
                 if e.startswith(prefix))
    glosses = (g.gloss for g in db.glosses
                       if g.gloss.startswith(prefix))
    for x in xrange(5):
        with ignore(StopIteration):
            suggestions.append(entries.next())
            types.append(db.entries[suggestions[-1]].type)
        with ignore(StopIteration):
            suggestions.append(glosses.next())
            types.append('gloss')
    return dumps([prefix, suggestions, types])


@route('/json/:entry')
def json(entry):
    if entry in db.entries:
        entry = db.entries[entry]
        word = entry.word
        type = entry.type
        affixes = entry.affixes
        grammarclass = entry.grammarclass
        definition = entry.definition
        notes = entry.notes
        del entry
        return locals()


@route('/:query#.*#')
@view('query')
@etag(db.etag)
def query(query):
    matches = set()
    
    entry = db.entries.get(query, None)
    if entry:    
        matches.add(entry)
    
    glosses = [g for g in db.glosses
                 if g.gloss == query
                 or g.gloss == query.capitalize()]
    matches.update(g.entry for g in glosses)
    
    affix = [e for e in db.entries.itervalues()
               if e not in matches
               and query in e.affixes]
    matches.update(affix)
    
    classes = [e for e in db.entries.itervalues()
                 if e.grammarclass == query]
    matches.update(classes)
    
    types = [e for e in db.entries.itervalues()
               if e.type == query]
    matches.update(types)
    
    regexquery = r'\b(%s|%s)\b' % (re.escape(query),
                                   re.escape(query.capitalize()))
    
    definitions = [e for e in db.entries.itervalues()
                     if e not in matches
                     and re.search(regexquery, e.definition)]
    matches.update(definitions)
    
    notes =  [e for e in db.entries.itervalues()
                if e not in matches
                and e.notes
                and re.search(regexquery, e.notes)]
    matches.update(notes)
    
    if not entry and len(matches) == 1:
        redirect('/%s' % matches.pop())
        return
    
    del matches
    del regexquery
    
    return locals()


if __name__ == '__main__':
    from optparse import OptionParser
    import bottle
    parser = OptionParser()
    parser.add_option('-p', '--port', action='store', type='int', default=8080,
                      help='Listen on this port')
    parser.add_option('-d', '--debug', action='store_true',
                      help='Enable debugging')
    parser.add_option('-r', '--reloader', action='store_true',
                      help='Reload modules when they are modified')
    options, args = parser.parse_args()
    bottle.debug(options.debug)
    bottle.run(port=options.port, reloader=options.reloader)

