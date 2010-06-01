
from flaskext.genshi import render_response

from vlasisku import app
from vlasisku.utils import etag


@app.route('/page/help')
@etag
def help():
    return render_response('help.html')

