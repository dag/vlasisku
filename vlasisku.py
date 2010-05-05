#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import with_statement

from bottle import route, view, request, redirect, response, abort, send_file
from utils import etag, ignore, compound2affixes
import db
from os.path import join, dirname
from simplejson import dumps
import re
from stemming.porter2 import stem


DEBUG = False
if __name__ == '__main__':
    from cli import options
    DEBUG = options.debug


@route('/')
@view('index')
@etag(db.etag, DEBUG)
def index():
    debug = DEBUG
    if 'query' in request.GET:
        redirect(request.GET['query'])
        return
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


@route('/opensearch/')
@view('opensearch')
def opensearch():
    response.content_type = 'application/xml'
    hostname = request.environ['HTTP_HOST']
    path = request.environ.get('REQUEST_URI', '/opensearch/')
    path = path.rpartition('opensearch/')[0]
    return locals()

@route('/suggest/:prefix#.*#')
def suggest(prefix):
    prefix = request.GET.get('q', prefix.replace('+', ' ')).decode('utf-8')
    suggestions = []
    types = []
    entries = (e for e in db.entries.iterkeys()
                 if e.startswith(prefix))
    glosses = (g.gloss for g in db.glosses
                       if g.gloss.startswith(prefix))
    classes = set(e.grammarclass for e in db.entries.itervalues()
                                 if e.grammarclass
                                 and e.grammarclass.startswith(prefix))
    for x in xrange(5):
        with ignore(StopIteration):
            suggestions.append(entries.next())
            types.append(db.entries[suggestions[-1]].type)
        with ignore(StopIteration):
            suggestions.append(glosses.next())
            types.append('gloss')
        with ignore(KeyError):
            suggestions.append(classes.pop())
            types.append('class')
    if 'q' in request.GET:
        return '\n'.join(suggestions)
    else:
        response.content_type = 'application/json'
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
@etag(db.etag, DEBUG)
def query(query):
    debug = DEBUG
    query = query.decode('utf-8').replace('+', ' ')
    querystem = stem(query.lower())
    matches = set()
    
    entry = db.entries.get(query, None)
    if entry:    
        matches.add(entry)
        components = None
        if entry.type == 'lujvo':
            components = [(a, [e for e in db.entries.itervalues()
                                 if a in e.searchaffixes][0])
                                 for a in compound2affixes(entry.word)]
            components = ['<a href="%s" title="%s">%s</a>' %
                            (e, e.definition, a)
                            for a, e in components]
    
    glosses = [g for g in db.gloss_stems.get(querystem, [])
                 if g.entry not in matches]
    matches.update(g.entry for g in glosses)
    
    affix = [e for e in db.entries.itervalues()
               if e not in matches
               and query in e.searchaffixes]
    matches.update(affix)
    
    classes = [e for e in db.entries.itervalues()
                 if e.grammarclass == query
                 or e.grammarclass
                 and re.split(r'[0-9*]', e.grammarclass)[0] == query]
    matches.update(classes)
    
    types = [e for e in db.entries.itervalues()
               if e.type == query]
    matches.update(types)
    
    definitions = [e for e in db.definition_stems.get(querystem, [])
                     if e not in matches]
    matches.update(definitions)
    
    notes = [e for e in db.note_stems.get(querystem, [])
               if e not in matches]
    matches.update(notes)
    
    if not entry and len(matches) == 1:
        redirect(matches.pop())
        return
    
    sourcemetaphor = []
    unknownaffixes = None
    if not matches:
        try:
            sourcemetaphor = [[e for e in db.entries.itervalues()
                                 if a in e.searchaffixes][0]
                                 for a in compound2affixes(query)]
        except IndexError:
            unknownaffixes = True
    
    return locals()


if __name__ == '__main__':
    import bottle
    bottle.debug(options.debug)
    bottle.run(port=options.port, reloader=options.reloader)

