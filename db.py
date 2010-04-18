#-*- coding:utf-8 -*-

from ordereddict import OrderedDict
from os.path import join, dirname
import yaml
import xml.etree.cElementTree as ElementTree
from utils import tex2html, braces2links
from hashlib import sha1


entries = OrderedDict()
glosses = []

with open(join(dirname(__file__), 'data', 'class-scales.yml')) as f:
    class_scales = yaml.load(f)

with open(join(dirname(__file__), 'data', 'cll.yml')) as f:
    cll = yaml.load(f)

with open(join(dirname(__file__), 'data', 'terminators.yml')) as f:
    terminators = yaml.load(f)


class Entry(object):
    word = None
    type = None
    affixes = None
    grammarclass = None
    terminator = None
    terminates = None
    cll = None
    definition = None
    notes = None
    
    # We need new lists for every instance.
    def __init__(self):
        self.affixes = []
        self.terminates = []
        self.cll = []
    
    def __str__(self):
        return self.word

class Gloss(object):
    gloss = None
    entry = None
    sense = None
    place = None


jbovlaste = ElementTree.parse(join(dirname(__file__), 'data', 'jbovlaste.xml'))
types = ('gismu', 'cmavo', 'cmavo cluster', 'lujvo', "fu'ivla",
         'experimental gismu', 'experimental cmavo', 'cmene')

for type in types:
    for valsi in jbovlaste.findall('//valsi'):
        if valsi.get('type') == type:
            entry = Entry()
            entry.type = type
            entry.word = valsi.get('word')
            
            for child in valsi.getchildren():
                text = child.text.encode('utf-8')
                if child.tag == 'rafsi':
                    entry.affixes.append(text)
                elif child.tag == 'selmaho':
                    entry.grammarclass = text
                    for grammarclass, terminator in terminators.iteritems():
                        if text == grammarclass:
                            entry.terminator = terminator
                        if text == terminator:
                            entry.terminates.append(grammarclass)
                    if text in cll:
                        for path in cll[text]:
                            section = '{0}.{1}'.format(*path)
                            link = 'http://dag.github.com/cll/{0}/{1}/'
                            entry.cll.append((section, link.format(*path)))
                elif child.tag == 'definition':
                    entry.definition = tex2html(text)
                elif child.tag == 'notes':
                    entry.notes = braces2links(tex2html(text))
            
            entries[entry.word] = entry

for word in jbovlaste.findall('//nlword'):
    gloss = Gloss()
    gloss.gloss = word.get('word').encode('utf-8')
    gloss.entry = entries[word.get('valsi')]
    if word.get('sense'):
        gloss.sense = word.get('sense').encode('utf-8')
    if word.get('place'):
        gloss.place = word.get('place').encode('utf-8')
    glosses.append(gloss)


with open(join(dirname(__file__), 'data', 'jbovlaste.xml')) as f:
    etag = sha1()
    etag.update(f.read())
    etag = etag.hexdigest()

