
from __future__ import with_statement

from fnmatch import fnmatch
from os.path import join, getmtime
import cPickle as pickle
import xml.etree.cElementTree as ElementTree
import re

from stemming.porter2 import stem
from ordereddict import OrderedDict
import yaml

from vlasisku.models import Entry, Gloss
from vlasisku.utils import parse_query, ignore, unique, load_yaml, \
                           tex2html, add_stems, braces2links


TYPES = (('gismu', 'Root words.'),
         ('cmavo', 'Particles.'),
         ('cmavo cluster', 'Particle combinations.'),
         ('lujvo', 'Compound words.'),
         ("fu'ivla", 'Loan words.'),
         ('experimental gismu', 'Non-standard root words.'),
         ('experimental cmavo', 'Non-standard particles.'),
         ('cmene', 'Names.'))


class DB(object):
    """Container for all the processed data.

    Attributes:

    entries
        An OrderedDict mapping entry names to Entry instances.
    glosses
        A list of Gloss instances.
    definition_stems
        A dict mapping stems in definitions to lists of Entry instances.
    note_stems
        A dict mapping stems in notes to lists of Entry instances.
    gloss_stems
        A dict mapping the stem of glosses to lists of Gloss instances.
    class_scales
        A dict mapping grammatical classes to font sizes in ems.
    cll
        A dict mapping grammatical classes to lists
        of ``[chapter, section]`` lists.
    terminators
        A dict mapping grammatical classes to terminating grammatical classes.
    etag
        A string that changes if the database changes.

    """

    entries = None
    glosses = None
    definition_stems = None
    note_stems = None
    gloss_stems = None
    class_scales = None
    cll = None
    terminators = None
    etag = None

    @classmethod
    def load(cls, root_path='./', cache='data/db.pickle', **kwargs):
        """Try to load a cached database, fall back on building a new one.

        ``kwargs`` are passed to :meth:`__init__`.

        """
        try:
            with open(join(root_path, cache)) as f:
                db = pickle.load(f)
            db.etag = str(getmtime(join(root_path, cache)))
        except IOError:
            db = cls(root_path, **kwargs)
            with open(join(root_path, cache), 'w') as f:
                pickle.dump(db, f, pickle.HIGHEST_PROTOCOL)
        return db

    def query(self, query):
        """

        >>> from vlasisku import db
        >>> len(db.query('class:UI4')['matches'])
        6
        """
        parsed_query = parse_query(query)
        matches = set()
        entry = self.entries.get(query, None)
        if entry:
            matches.add(entry)

        if parsed_query['all']:
            words = []

            glosses = self.matches_gloss(parsed_query['all'], matches)
            matches.update(g.entry for g in glosses)

            affix = self.matches_affix(parsed_query['all'], matches)
            matches.update(affix)

            classes = self.matches_class(parsed_query['all'], matches)
            classes += [e for e in self.entries.itervalues()
                          if e.grammarclass
                          and e not in classes
                          and re.split(r'[0-9*]', e.grammarclass)[0] == query]
            matches.update(classes)

            types = self.matches_type(parsed_query['all'], matches)
            matches.update(types)

            definitions = self.matches_definition(parsed_query['all'], matches)
            matches.update(definitions)

            notes = self.matches_notes(parsed_query['all'], matches)
            matches.update(notes)

        else:
            words = self.matches_word(parsed_query['word'])
            matches.update(words)

            glosses = self.matches_gloss(parsed_query['gloss'], matches)
            matches.update(g.entry for g in glosses)

            affix = self.matches_affix(parsed_query['affix'], matches)
            matches.update(affix)

            classes = self.matches_class(parsed_query['class'], matches)
            matches.update(classes)

            types = self.matches_type(parsed_query['type'], matches)
            matches.update(types)

            definitions = self.matches_definition(parsed_query['definition'], matches)
            matches.update(definitions)

            notes = self.matches_notes(parsed_query['notes'], matches)
            matches.update(notes)

        if parsed_query['word']:
            matches = set(e for e in self.matches_word(parsed_query['word'])
                            if e in matches)
        if parsed_query['gloss']:
            matches = set(g.entry for g in self.matches_gloss(parsed_query['gloss'])
                                  if e in matches)
        if parsed_query['affix']:
            matches = set(e for e in self.matches_affix(parsed_query['affix'])
                            if e in matches)
        if parsed_query['class']:
            matches = set(e for e in self.matches_class(parsed_query['class'])
                            if e in matches)
        if parsed_query['type']:
            matches = set(e for e in self.matches_type(parsed_query['type'])
                            if e in matches)
        if parsed_query['definition']:
            matches = set(e for e
                            in self.matches_definition(parsed_query['definition'])
                            if e in matches)
        if parsed_query['notes']:
            matches = set(e for e in self.matches_notes(parsed_query['notes'])
                            if e in matches)

        words = [e for e in words if e in matches]
        glosses = [g for g in glosses if g.entry in matches]
        affix = [e for e in affix if e in matches]
        classes = [e for e in classes if e in matches]
        types = [e for e in types if e in matches]
        definitions = [e for e in definitions if e in matches]
        notes = [e for e in notes if e in matches]

        results = dict(locals())
        del results['self']
        return results

    def suggest(self, prefix):
        suggestions = []
        types = []
        entries = (e for e in self.entries.iterkeys()
                     if e.startswith(prefix))
        glosses = (g.gloss for g in self.glosses
                           if g.gloss.startswith(prefix))
        classes = set(e.grammarclass for e in self.entries.itervalues()
                                     if e.grammarclass
                                     and e.grammarclass.startswith(prefix))
        for x in xrange(5):
            with ignore(StopIteration):
                suggestions.append(entries.next())
                types.append(self.entries[suggestions[-1]].type)
            with ignore(StopIteration):
                gloss = glosses.next()
                if ' ' in gloss:
                    suggestions.append('"%s"' % gloss)
                else:
                    suggestions.append(gloss)
                types.append('gloss')
            with ignore(KeyError):
                suggestions.append(classes.pop())
                types.append('class')
        return [prefix, suggestions, types]

    def matches_word(self, queries):
        return list(unique(e for q in queries
                             for e in self.entries.itervalues()
                             if fnmatch(e.word, q)))

    def matches_gloss(self, queries, exclude=set()):
        return list(unique(g for q in queries
                             for g in self.gloss_stems.get(stem(q.lower()), [])
                             if all(g in self.gloss_stems.get(
                                stem(q.lower()), []) for q in queries)
                             if g.entry not in exclude))

    def matches_affix(self, queries, exclude=set()):
        return list(unique(e for e in self.entries.itervalues()
                             if e not in exclude
                             for q in queries
                             if any(fnmatch(a, q) for a in e.searchaffixes)))

    def matches_class(self, queries, exclude=set()):
        return list(unique(e for q in queries
                             for e in self.entries.itervalues()
                             if e not in exclude
                             if q == e.grammarclass))

    def matches_type(self, queries, exclude=set()):
        return list(unique(e for q in queries
                             for e in self.entries.itervalues()
                             if e not in exclude
                             if fnmatch(e.type, q)))

    def matches_definition(self, queries, exclude=set()):
        return list(unique(e for q in queries
                             for e in self.definition_stems.get(
                                stem(q.lower()), [])
                             if all(e in self.definition_stems.get(
                                stem(q.lower()), []) for q in queries)
                             if e not in exclude))

    def matches_notes(self, queries, exclude=set()):
        return list(unique(e for q in queries
                             for e in self.note_stems.get(stem(q.lower()), [])
                             if all(e in self.note_stems.get(
                                stem(q.lower()), []) for q in queries)
                             if e not in exclude))

    def __init__(self, root_path='./',
                 jbovlaste='data/jbovlaste.xml',
                 class_scales='data/class-scales.yml',
                 cll='data/cll.yml',
                 terminators='data/terminators.yml'):
        """Build a database from the data files."""

        self.class_scales = load_yaml(join(root_path, class_scales))
        self.cll = load_yaml(join(root_path, cll))
        self.terminators = load_yaml(join(root_path, terminators))

        with open(join(root_path, jbovlaste)) as f:
            xml = ElementTree.parse(f)
            self._load_entries(xml)
            self._load_glosses(xml)

        self.etag = str(getmtime(join(root_path, jbovlaste)))


    def _load_entries(self, xml):
        processors = {'rafsi': self._process_rafsi,
                      'selmaho': self._process_selmaho,
                      'definition': self._process_definition,
                      'notes': self._process_notes}

        self.entries = OrderedDict()
        self.definition_stems = {}
        self.note_stems = {}

        for type, _ in TYPES:
            for valsi in xml.findall('//valsi'):
                if valsi.get('type') == type:
                    entry = Entry(self)
                    entry.type = type
                    entry.word = valsi.get('word')

                    if type in ('gismu', 'experimental gismu'):
                        entry.searchaffixes.append(entry.word)
                        entry.searchaffixes.append(entry.word[0:4])

                    for child in valsi.getchildren():
                        tag, text = child.tag, child.text
                        processors.get(tag, lambda: None)(entry, text)

                    self.entries[entry.word] = entry

        for entry in self.entries.itervalues():
            if entry.notes:
                entry.notes = braces2links(entry.notes, self.entries)


    def _process_rafsi(self, entry, text):
        entry.affixes.append(text)
        entry.searchaffixes.append(text)

    def _process_selmaho(self, entry, text):
        entry.grammarclass = text
        for grammarclass, terminator in self.terminators.iteritems():
            if text == grammarclass:
                entry.terminator = terminator
            if text == terminator:
                entry.terminates.append(grammarclass)
        if text in self.cll:
            for path in self.cll[text]:
                section = '%s.%s' % tuple(path)
                link = 'http://dag.github.com/cll/%s/%s/'
                entry.cll.append((section, link % tuple(path)))

    def _process_definition(self, entry, text):
        entry.definition = tex2html(text)
        tokens = re.findall(r"[\w']+", text, re.UNICODE)
        for token in set(tokens):
            add_stems(token, self.definition_stems, entry)

    def _process_notes(self, entry, text):
        entry.notes = tex2html(text)
        tokens = re.findall(r"[\w']+", text, re.UNICODE)
        for token in set(tokens):
            add_stems(token, self.note_stems, entry)


    def _load_glosses(self, xml):
        self.glosses = []
        self.gloss_stems = {}
        for type, _ in TYPES:
            for word in xml.findall('//nlword'):
                entry = self.entries[word.get('valsi')]
                if entry.type == type:
                    gloss = Gloss()
                    gloss.gloss = word.get('word')
                    gloss.entry = entry
                    gloss.sense = word.get('sense')
                    gloss.place = word.get('place')
                    self.glosses.append(gloss)
                    add_stems(gloss.gloss, self.gloss_stems, gloss)
