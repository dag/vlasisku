
from flask import Flask
from flaskext.genshi import Genshi

from vlasisku.database import DB


app = Flask(__name__)
db = DB.load(app.root_path)
genshi = Genshi(app)

ETAG = db.etag

app.config.from_object(__name__)

genshi.extensions['js'] = 'js'
genshi.methods['js'] = {
    'mimetype': 'application/javascript',
    'serializer': 'text',
    'class': genshi.methods['text']['class']
}

import vlasisku.views

