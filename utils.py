#-*- coding:utf-8 -*-

from string import Template
import re
from stemming.porter2 import stem
from bottle import response, request, abort
from contextlib import contextmanager


def compound2affixes(compound):
    c = r'[bcdfgjklmnprstvxz]'
    v = r'[aeiou]'
    cc = r'(?:'
    cc += r'bl|br|'
    cc += r'cf|ck|cl|cm|cn|cp|cr|ct|'
    cc += r'dj|dr|dz|fl|fr|gl|gr|'
    cc += r'jb|jd|jg|jm|jv|kl|kr|'
    cc += r'ml|mr|pl|pr|'
    cc += r'sf|sk|sl|sm|sn|sp|sr|st|'
    cc += r'tc|tr|ts|vl|vr|xl|xr|'
    cc += r'zb|zd|zg|zm|zv)'
    vv = r'(?:ai|ei|oi|au)'
    rafsi3v = Template(r"(?:$cc$v|$c$vv|$c$v'$v)").substitute(locals())
    rafsi3 = Template(r'(?:$rafsi3v|$c$v$c)').substitute(locals())
    rafsi4 = Template(r'(?:$c$v$c$c|$cc$v$c)').substitute(locals())
    rafsi5 = Template(r'$rafsi4$v').substitute(locals())
    
    for i in xrange(1, len(compound)/3+1):
        reg = Template(r'(?:($rafsi3)[nry]??|($rafsi4)y)')
        reg = reg.substitute(locals()) * i
        reg2 = Template(r'^$reg($rafsi3v|$rafsi5)$$').substitute(locals())
        matches = re.findall(reg2, compound)
        if matches:
            return [r for r in matches[0] if r]
    
    return []


def tex2html(tex):
    """Turn most of the TeX used in jbovlaste into HTML.
    
    >>> tex2html('$x_1$ is $10^2*2$ examples of $x_{2}$.')
    u'x<sub>1</sub> is 10<sup>2\\xd72</sup> examples of x<sub>2</sub>.'
    >>> tex2html('\emph{This} is emphasised and \\\\textbf{this} is boldfaced.')
    u'<em>This</em> is emphasised and <strong>this</strong> is boldfaced.'
    """
    def math(m):
        t = []
        for x in m.group(1).split('='):
            x = x.replace('{', '').replace('}', '')
            x = x.replace('*', u'×')
            if '_' in x:
                t.append(u'%s<sub>%s</sub>' % tuple(x.split('_')[0:2]))
            elif '^' in x:
                t.append(u'%s<sup>%s</sup>' % tuple(x.split('^')[0:2]))
            else:
                t.append(x)
        return '='.join(t)
    def typography(m):
        if m.group(1) == 'emph':
            return u'<em>%s</em>' % m.group(2)
        elif m.group(1) == 'textbf':
            return u'<strong>%s</strong>' % m.group(2)
    tex = re.sub(r'\$(.+?)\$', math, tex)
    tex = re.sub(r'\\(emph|textbf)\{(.+?)\}', typography, tex)
    return tex

def braces2links(text, entries):
    """Turns {quoted words} into HTML links.
    
    >>> import db
    >>> braces2links('See also {mupli}.', db.entries)
    u'See also <a href="mupli" title="x<sub>1</sub> is
    an example/sample/specimen/instance/case/illustration of
    common property(s) x<sub>2</sub> of set x<sub>3</sub>.">mupli</a>.'
    >>> braces2links('See also {missing}.', db.entries)
    u'See also <a
    href="http://jbovlaste.lojban.org/dict/addvalsi.html?valsi=missing"
    title="This word is missing, please add it!" class="missing">missing</a>.'
    """
    def f(m):
        try:
            values = (m.group(1), entries[m.group(1)].definition, m.group(1))
            return u'<a href="%s" title="%s">%s</a>' % values
        except KeyError:
            link = [u'<a href="']
            link.append(u'http://jbovlaste.lojban.org')
            link.append(u'/dict/addvalsi.html?valsi=%s"')
            link.append(u' title="This word is missing, please add it!"')
            link.append(u' class="missing">%s</a>')
            return ''.join(link) % (m.group(1), m.group(1))
    return re.sub(r'\{(.+?)\}', f, text)


def add_stems(token, collection, item):
    stemmed = stem(token.lower())
    if stemmed not in collection:
        collection[stemmed] = []
    if item not in collection[stemmed]:
        collection[stemmed].append(item)


def etag(tag, debug=False):
    """Decorator to add ETag handling to a callback."""
    def decorator(f):
        def wrapper(**kwargs):
            response.header['ETag'] = tag
            if request.environ.get('HTTP_IF_NONE_MATCH', None) == tag:
                if not debug:
                    abort(304)
                    return
            return f(**kwargs)
        return wrapper
    return decorator


@contextmanager
def ignore(exc):
    """Context manager to ignore an exception."""
    try:
        yield
    except exc:
        pass


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)

