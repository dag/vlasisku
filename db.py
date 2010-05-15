#-*- coding:utf-8 -*-

from __future__ import with_statement

from os.path import join, dirname
import xml.etree.cElementTree as ElementTree
from os import stat
import re

from ordereddict import OrderedDict
import yaml

from models import Entry, Gloss
from utils import tex2html, braces2links, add_stems


entries = OrderedDict()
glosses = []
definition_stems = {}
note_stems = {}
gloss_stems = {}

with open(join(dirname(__file__), 'data', 'class-scales.yml')) as f:
    class_scales = yaml.load(f)

with open(join(dirname(__file__), 'data', 'cll.yml')) as f:
    cll = yaml.load(f)

with open(join(dirname(__file__), 'data', 'terminators.yml')) as f:
    terminators = yaml.load(f)


jbovlaste = ElementTree.parse(join(dirname(__file__), 'data', 'jbovlaste.xml'))
types = ('gismu', 'cmavo', 'cmavo cluster', 'lujvo', "fu'ivla",
         'experimental gismu', 'experimental cmavo', 'cmene')

for type in types:
    for valsi in jbovlaste.findall('//valsi'):
        if valsi.get('type') == type:
            entry = Entry()
            entry.type = type
            entry.word = valsi.get('word')

            if type in ('gismu', 'experimental gismu'):
                entry.searchaffixes.append(entry.word)
                entry.searchaffixes.append(entry.word[0:4])
            
            for child in valsi.getchildren():
                text = child.text
                
                if child.tag == 'rafsi':
                    entry.affixes.append(text)
                    entry.searchaffixes.append(text)
                
                elif child.tag == 'selmaho':
                    entry.grammarclass = text
                    for grammarclass, terminator in terminators.iteritems():
                        if text == grammarclass:
                            entry.terminator = terminator
                        if text == terminator:
                            entry.terminates.append(grammarclass)
                    if text in cll:
                        for path in cll[text]:
                            section = '%s.%s' % tuple(path)
                            link = 'http://dag.github.com/cll/%s/%s/'
                            entry.cll.append((section, link % tuple(path)))
                
                elif child.tag == 'definition':
                    entry.definition = tex2html(text)
                    for token in set(re.findall(r"[\w']+", text, re.UNICODE)):
                        add_stems(token, definition_stems, entry)
                
                elif child.tag == 'notes':
                    entry.notes = tex2html(text)
                    for token in set(re.findall(r"[\w']+", text, re.UNICODE)):
                        add_stems(token, note_stems, entry)
            
            entries[entry.word] = entry

for entry in entries.itervalues():
    if entry.notes:
        entry.notes = braces2links(entry.notes, entries)

for type in types:
    for word in jbovlaste.findall('//nlword'):
        entry = entries[word.get('valsi')]
        if entry.type == type:
            gloss = Gloss()
            gloss.gloss = word.get('word')
            gloss.entry = entry
            if word.get('sense'):
                gloss.sense = word.get('sense')
            if word.get('place'):
                gloss.place = word.get('place')
            glosses.append(gloss)
            add_stems(gloss.gloss, gloss_stems, gloss)


etag = str(stat(join(dirname(__file__), 'data', 'jbovlaste.xml')).st_mtime)

