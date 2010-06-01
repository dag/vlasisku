
from flask import send_file

from vlasisku import app


@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')

