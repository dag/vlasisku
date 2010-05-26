
from genshi.template import TemplateLoader, loader


class GenshiTemplater(object):

    types = {'html': dict(serializer='html', doctype='html',
                          mimetype='text/html'),
             'html5': dict(serializer='html', doctype='html5',
                           mimetype='text/html'),
             'xhtml': dict(serializer='xhtml', doctype='xhtml',
                           mimetype='application/xhtml+xml'),
             'xml': dict(serializer='xml', mimetype='application/xml'),
             'text': dict(serializer='text', mimetype='text/plain')}

    def __init__(self, app, type='html'):
        """Set up a Genshi template loader
        based on your Flask app configuration.

        """
        path = loader.package(app.import_name, 'templates')
        auto_reload = app.jinja_env.auto_reload
        self.loader = TemplateLoader(path, auto_reload=auto_reload)
        self.app = app
        self.type = type

    def template(self, template, context={}, serializer='html', doctype='html'):
        """Render a template, by default as HTML."""
        tmpl = self.loader.load(template)
        context.update(self.app.jinja_env.globals)
        if not doctype:
            return tmpl.generate(**context).render(serializer)
        return tmpl.generate(**context).render(serializer, doctype=doctype)

    def response(self, template, context={}, type=None):
        """Render to a Response with correct mimetype."""
        type = self.types[type] if type is not None else self.types[self.type]
        doctype = type['doctype'] if 'doctype' in type else None
        body = self.template(template, context, type['serializer'], doctype)
        return self.app.response_class(body, mimetype=type['mimetype'])

