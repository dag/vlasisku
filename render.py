
from genshi.template import TemplateLoader, loader


class GenshiTemplater(object):

    def __init__(self, app):
        """Set up a Genshi template loader
        based on your Flask app configuration.
        
        """
        path = loader.package(app.import_name, 'templates')
        auto_reload = app.jinja_env.auto_reload
        self.loader = TemplateLoader(path, auto_reload=auto_reload)
        self.app = app

    def template(self, template, context={}, serializer='html', doctype='html'):
        """Render a template, by default as HTML."""
        tmpl = self.loader.load(template)
        context.update(self.app.jinja_env.globals)
        if not doctype:
            return tmpl.generate(**context).render(serializer)
        return tmpl.generate(**context).render(serializer, doctype=doctype)

    def html(self, template, context={}):
        """Render a template as HTML."""
        return self.template(template, context, 'html', 'html')

    def html5(self, template, context={}):
        """Render a template as HTML5."""
        return self.template(template, context, 'html', 'html5')

    def xhtml(self, template, context={}):
        """Render a template as XHTML."""
        return self.template(template, context, 'xhtml', 'xhtml')

    def xml(self, template, context={}):
        """Render a template as XML."""
        return self.template(template, context, 'xml', None)

    def text(self, template, context={}):
        """Render a template as text."""
        return self.template(template, context, 'text', None)

