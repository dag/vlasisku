from utils import compound2affixes
import dbpickler as db


class Entry(object):
    word = None
    type = None
    affixes = None
    searchaffixes = None
    grammarclass = None
    terminator = None
    terminates = None
    cll = None
    definition = None
    notes = None
    
    # We need new lists for every instance.
    def __init__(self):
        self.affixes = []
        self.searchaffixes = []
        self.terminates = []
        self.cll = []
    
    def __str__(self):
        return self.word
    
    def components(self):
        if self.type == 'lujvo':
            components = ''
            for a in compound2affixes(self.word):
                if len(a) == 1:
                    components += a
                else:
                    word = [e for e in db.entries.itervalues()
                              if a in e.searchaffixes].pop()
                    components += '<a href="%s" ' % word
                    components += 'title="<strong>%s:</strong> ' % word
                    components += '%s">%s</a>' % (word.definition, a)
            return components


class Gloss(object):
    gloss = None
    entry = None
    sense = None
    place = None

