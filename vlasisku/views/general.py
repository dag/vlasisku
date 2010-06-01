
from flask import send_file
from flaskext.genshi import render_response

from vlasisku import app


@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')


@app.route('/custom.js')
def javascript():
    return render_response('custom.js')

