from genshi.template import TemplateLoader
from os.path import join, dirname


class Render(object):
    
    def __init__(self, auto_reload=False):
        self.loader = TemplateLoader(join(dirname(__file__), 'templates'),
                                     auto_reload=auto_reload)

    def html(self, template, context):
        tmpl = self.loader.load('%s.xml' % template)
        return tmpl.generate(**context).render('html', doctype='html')

    def xml(self, template, context):
        tmpl = self.loader.load('%s.xml' % template)
        return tmpl.generate(**context).render('xml')

