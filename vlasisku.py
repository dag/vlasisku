#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import with_statement

import re

from flask import Flask, request, redirect, send_file, Response, json, url_for
from stemming.porter2 import stem

from db import DB, TYPES
from utils import etag, parse_query, compound2affixes, dameraulevenshtein
from render import GenshiTemplater


app = Flask(__name__)
db = DB.load(app.root_path)

app.debug = __name__ == '__main__'
app.jinja_env.auto_reload = app.debug
app.etag = db.etag

render = GenshiTemplater(app)


@app.route('/')
@etag
def index():
    showgrid = 'showgrid' in request.args
    if 'query' in request.args:
        return redirect(request.args.get('query'))
    types = TYPES
    classes = set(e.grammarclass for e in db.entries.itervalues()
                                 if e.grammarclass)
    scales = db.class_scales
    return render.html('index.xml', locals())


@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico', 'image/x-icon')


@app.route('/opensearch/')
def opensearch():
    return Response(render.xml('opensearch.xml'), mimetype='application/xml')

@app.route('/suggest/<prefix>')
def suggest(prefix):
    return Response(json.dumps(db.suggest(prefix)), mimetype='application/json')

@app.route('/_complete/')
def complete():
    return '\n'.join(db.suggest(request.args.get('q', ''))[1])


@app.route('/<query>')
@etag
def query(query):
    showgrid = 'showgrid' in request.args
    query = query.replace('+', ' ')
    parsed_query = parse_query(query)
    matches = set()

    entry = db.entries.get(query, None)
    if entry:
        matches.add(entry)

    glosses = []
    for q in parsed_query['gloss']:
        for g in db.gloss_stems.get(stem(q.lower()), []):
            if g.entry not in matches:
                glosses.append(g)
                matches.add(g.entry)

    affix = [e for e in db.entries.itervalues()
               if e not in matches
               and any(q in e.searchaffixes for q in parsed_query['affix'])]
    matches.update(affix)

    classes = [e for e in db.entries.itervalues()
                 if any(q == e.grammarclass for q in parsed_query['class'])
                 or e.grammarclass
                 and re.split(r'[0-9*]', e.grammarclass)[0] == query]
    matches.update(classes)

    types = [e for e in db.entries.itervalues()
               if any(q == e.type for q in parsed_query['type'])]
    matches.update(types)

    definitions = []
    for q in parsed_query['definition']:
        for e in db.definition_stems.get(stem(q.lower()), []):
            if e not in matches:
                definitions.append(e)
                matches.add(e)

    notes = []
    for q in parsed_query['notes']:
        for e in db.note_stems.get(stem(q.lower()), []):
            if e not in matches:
                notes.append(e)
                matches.add(e)

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

    return render.html('query.xml', locals())


if __name__ == '__main__':
    app.run()

