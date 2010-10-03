
from flask import Flask
from flaskext.genshi import Genshi

from vlasisku.database import Database


app = Flask(__name__)
db = Database(app).root
genshi = Genshi(app)

ETAG = db.etag

app.config.from_object(__name__)


import vlasisku.views
