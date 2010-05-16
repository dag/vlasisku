from utils import compound2affixes


class Entry(object):
    """Container for jbovlaste entry data.

    Attributes:

    word
        The word (or compound) this entry describes.
    type
        The type of the word, such as ``'gismu'``.
    affixes
        A list of three-letter affix forms for the word.
    searchaffixes
        A list of affixes including four and five-letter versions.
    grammarclass
        The grammatical class if the word is a particle.
    terminator
        The grammatical class of this words terminator, if any.
    terminates
        A list of grammatical classes this word terminates, for terminators.
    cll
        A list of two-tuples such as ``('<chapter>.<section>', 'http://...')``.
    definition
        The entry definition, such as a place structure.
    notes
        Notes about the entry.
    db
        The :class:`~db.DB` instance this entry is in.

    """

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
    db = None

    # We need new lists for every instance.
    def __init__(self, db):
        self.affixes = []
        self.searchaffixes = []
        self.terminates = []
        self.cll = []
        self.db = db

    def __str__(self):
        return self.word

    def components(self):
        """Build HTML that links the affixes in a compound
        to their corresponding words, with definitions in the link tooltips.

        """
        if self.type == 'lujvo':
            components = ''
            for a in compound2affixes(self.word):
                if len(a) == 1:
                    components += a
                else:
                    word = [e for e in self.db.entries.itervalues()
                              if a in e.searchaffixes].pop()
                    components += '<a href="%s" ' % word
                    components += 'title="<strong>%s:</strong> ' % word
                    components += '%s">%s</a>' % (word.definition, a)
            return components


class Gloss(object):
    """Container for jbovlaste gloss data.

    Attributes:

    gloss
        The actual gloss word.
    entry
        The :class:`Entry` this glosses to.
    sense
        The sense in which this gloss word relates to the entry, or ``None``.
    place
        The specific place of the entry this glosses to, if any.

    """

    gloss = None
    entry = None
    sense = None
    place = None

