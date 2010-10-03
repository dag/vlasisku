
from flask import Module, current_app, json
from flaskext.genshi import render_response

from vlasisku.extensions import database


os = Module(__name__)


@os.route('/opensearch/')
def opensearch():
    return render_response('opensearch.xml')


@os.route('/suggest/<prefix>')
def suggest(prefix):
    cls = current_app.response_class
    return cls(json.dumps(database.root.suggest(prefix)),
               mimetype='application/json')
