
from __future__ import with_statement

from os.path import join, dirname
import cPickle as pickle
from models import Entry, Gloss
from os import stat


try:
    with open(join(dirname(__file__), 'data', 'db.pickle')) as f:
        data = pickle.load(f)
    entries = data['entries']
    glosses = data['glosses']
    definition_stems = data['definition_stems']
    note_stems = data['note_stems']
    gloss_stems = data['gloss_stems']
    class_scales = data['class_scales']
    cll = data['cll']
    terminators = data['terminators']
    etag = str(stat(join(dirname(__file__), 'data', 'jbovlaste.xml')).st_mtime)

except IOError:
    from db import *
    data = dict(entries=entries,
                glosses=glosses,
                definition_stems=definition_stems,
                note_stems=note_stems,
                gloss_stems=gloss_stems,
                class_scales=class_scales,
                cll=cll,
                terminators=terminators)
    with open(join(dirname(__file__), 'data', 'db.pickle'), 'w') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

