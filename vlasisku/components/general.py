
from flask import Module, send_file
from flaskext.genshi import render_response


general = Module(__name__)


@general.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')


@general.route('/custom.js')
def javascript():
    return render_response('custom.js')
