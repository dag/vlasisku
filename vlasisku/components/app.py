
from flask import Module, request, redirect, url_for
from flaskext.genshi import render_response

from vlasisku.extensions import database
from vlasisku.utils import etag, compound2affixes, dameraulevenshtein
from vlasisku.database import TYPES


app = Module(__name__)


@app.route('/')
@etag
def index():
    db = database.root
    if 'query' in request.args:
        return redirect(request.args.get('query'))
    types = TYPES
    classes = set(e.grammarclass for e in db.entries.itervalues()
                                 if e.grammarclass)
    scales = db.class_scales
    return render_response('index.html', locals())


@app.route('/<query>')
@etag
def query(query):
    db = database.root
    query = query.replace('+', ' ')
    results = db.query(query)

    if not results['entry'] and len(results['matches']) == 1:
        return redirect(url_for('query', query=results['matches'].pop()))

    sourcemetaphor = []
    unknownaffixes = None
    similar = None
    if not results['matches']:
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

    results.update(locals())
    return render_response('query.html', results)


@app.route('/_complete/')
def complete():
    return '\n'.join(database.root.suggest(request.args.get('q', ''))[1])
