
from flask import Module
from flaskext.genshi import render_response

from vlasisku.utils import etag


pages = Module(__name__)


@pages.route('/help')
@etag
def help():
    return render_response('help.html')
