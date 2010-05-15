#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import with_statement

import re

from flask import Flask, request, redirect, send_file, Response, \
                  json, jsonify, url_for
from stemming.porter2 import stem

from utils import etag, ignore, compound2affixes, dameraulevenshtein
import dbpickler as db
from render import Render


app = Flask(__name__)
app.debug = __name__ == '__main__'
render = Render(app.debug)


@app.route('/')
@etag(db.etag, app.debug)
def index():
    showgrid = 'showgrid' in request.args
    if 'query' in request.args:
        return redirect(request.args.get('query'))
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
    return render.html('index', locals())


@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico', 'image/x-icon')


@app.route('/opensearch/')
def opensearch():
    hostname = request.environ['HTTP_HOST']
    path = request.environ.get('REQUEST_URI', '/opensearch/')
    path = path.rpartition('opensearch/')[0]
    return Response(render.xml('opensearch', locals()),
                    mimetype='application/xml')

@app.route('/suggest/')
@app.route('/suggest/<prefix>')
def suggest(prefix=''):
    prefix = request.args.get('q', prefix.replace('+', ' ')).decode('utf-8')
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
    if 'q' in request.args:
        return '\n'.join(suggestions)
    else:
        return Response(json.dumps([prefix, suggestions, types]),
                        mimetype='application/json')


@app.route('/json/<entry>')
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
        return jsonify(locals())


@app.route('/<query>')
@etag(db.etag, app.debug)
def query(query):
    showgrid = 'showgrid' in request.args
    query = query.decode('utf-8').replace('+', ' ')
    querystem = stem(query.lower())
    matches = set()
    
    entry = db.entries.get(query, None)
    if entry:    
        matches.add(entry)
    
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
        return redirect(url_for('query', query=matches.pop()))
    
    sourcemetaphor = []
    unknownaffixes = None
    similar = None
    if not matches:
        try:
            sourcemetaphor = [[e for e in db.entries.itervalues()
                                 if a in e.searchaffixes].pop()
                                 for a in compound2affixes(query)
                                 if len(a) != 1]
        except IndexError:
            unknownaffixes = True
        
        similar = [e.word for e in db.entries.itervalues()
                          if e not in matches
                          and dameraulevenshtein(query, e.word) == 1]
        
        similar += [g.gloss for g in db.glosses
                            if g.entry not in matches
                            and g.gloss not in similar
                            and dameraulevenshtein(query, g.gloss) == 1]
    
    return render.html('query', locals())


if __name__ == '__main__':
    app.run()

