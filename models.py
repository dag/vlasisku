
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


class Gloss(object):
    gloss = None
    entry = None
    sense = None
    place = None

