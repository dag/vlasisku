
from flaskext.genshi import render_response
from flask import json

from vlasisku import app, db


@app.route('/opensearch/')
def opensearch():
    return render_response('opensearch.xml')


@app.route('/suggest/<prefix>')
def suggest(prefix):
    return app.response_class(json.dumps(db.suggest(prefix)),
                              mimetype='application/json')

