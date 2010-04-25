#-*- coding:utf-8 -*-

import re
from bottle import response, request, abort
from contextlib import contextmanager


def tex2html(tex):
    """Turn most of the TeX used in jbovlaste into HTML.
    
    >>> tex2html('$x_1$ is $10^2$ examples of $x_{2}$.')
    'x<sub>1</sub> is 10<sup>2</sup> examples of x<sub>2</sub>.'
    """
    def math(m):
        t = []
        for x in m.group(1).split('='):
            x = x.replace('{', '').replace('}', '')
            x = x.replace('*', u'×'.encode('utf-8'))
            if '_' in x:
                t.append('%s<sub>%s</sub>' % tuple(x.split('_')[0:2]))
            elif '^' in x:
                t.append('%s<sup>%s</sup>' % tuple(x.split('^')[0:2]))
            else:
                t.append(x)
        return '='.join(t)
    def typography(m):
        if m.group(1) == 'emph':
            return '<em>%s</em>' % m.group(2)
        elif m.group(1) == 'textbf':
            return '<strong>%s</strong>' % m.group(2)
    tex = re.sub(r'\$(.+?)\$', math, tex)
    tex = re.sub(r'\\(emph|textbf)\{(.+?)\}', typography, tex)
    return tex

def braces2links(text, entries):
    """Turns {quoted words} into HTML links.
    
    >>> braces2links("See also {mupli}, {mu'u}.")
    'See also <a href="mupli">mupli</a>, <a href="mu\\'u">mu\\'u</a>.'
    """
    def f(m):
        try:
            values = (m.group(1), entries[m.group(1)].definition, m.group(1))
            return '<a href="%s" title="%s">%s</a>' % values
        except KeyError:
            link = ['<a href="']
            link.append('http://jbovlaste.lojban.org')
            link.append('/dict/addvalsi.html?valsi=%s"')
            link.append(' title="This word is missing, please add it!"')
            link.append(' class="missing">%s</a>')
            return ''.join(link) % (m.group(1), m.group(1))
    return re.sub(r'\{(.+?)\}', f, text)


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
    doctest.testmod()

