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

    glosses = [g for g in db.gloss_stems.get(stem(query), [])
                 if g.entry not in matches]
    matches.update(g.entry for g in glosses)

    affix = [e for e in db.entries.itervalues()
               if e not in matches
               for q in parsed_query['affix']
               if q in e.searchaffixes]
    matches.update(affix)

    classes = [e for q in parsed_query['class']
                 for e in db.entries.itervalues()
                 if q == e.grammarclass
                 or e.grammarclass
                 and re.split(r'[0-9*]', e.grammarclass)[0] == query]
    matches.update(classes)

    types = [e for e in db.entries.itervalues()
               if query == e.type]
    matches.update(types)

    definitions = [e for q in parsed_query['definition']
                     for e in db.definition_stems.get(stem(q.lower()), [])
                     if e not in matches]
    matches.update(definitions)

    notes = [e for q in parsed_query['notes']
               for e in db.note_stems.get(stem(q.lower()), [])
               if e not in matches]
    matches.update(notes)

    if not entry and len(matches) == 1:
        return redirect(url_for('query', query=matches.pop()))

    sourcemetaphor = []
    unknownaffixes = None
    similar = None
    if not matches:
        sourcemetaphor = [e for a in compound2affixes(query)
                            if len(a) != 1
                            for e in db.entries.itervalues()
                            if a in e.searchaffixes]

        unknownaffixes = len(sourcemetaphor) != \
                         len([a for a in compound2affixes(query)
                                if len(a) != 1])

        similar = [e.word for e in db.entries.itervalues()
                          if dameraulevenshtein(query, e.word) == 1]

        similar += [g.gloss for g in db.glosses
                            if g.gloss not in similar
                            and dameraulevenshtein(query, g.gloss) == 1]

    return render.html('query.xml', locals())


if __name__ == '__main__':
    app.run()

