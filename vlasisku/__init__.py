
from flask import Flask
from flaskext.genshi import Genshi

from vlasisku.database import DB


app = Flask(__name__)
db = DB.load(app.root_path)
genshi = Genshi(app)

ETAG = db.etag

app.config.from_object(__name__)


import vlasisku.views

