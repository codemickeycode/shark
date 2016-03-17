import inspect

import time
from types import new_class

import bleach
import markdown
from collections import Iterable
from django.conf.urls import url
import json

from django.core import urlresolvers
from django.core.urlresolvers import reverse, get_resolver, RegexURLResolver, RegexURLPattern, NoReverseMatch
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.test import Client
from django.test import TestCase
from django.utils.html import escape
from django.utils.timezone import now
from django.views.static import serve

from shark import models
from shark.analytics import GoogleAnalyticsTracking
from shark.layout import Div
from shark.layout import Row
from shark.models import EditableText, StaticPage as StaticPageModel
from shark.ui_elements import BreadCrumbs
from .base import Collection, BaseObject, PlaceholderWebObject, Default, ALLOWED_TAGS, ALLOWED_ATTRIBUTES, \
    ALLOWED_STYLES, Markdown
from .resources import Resources

unique_name_counter = 0

class BaseHandler:
    enable_amp = False
    route = None

    def __init__(self, *args, **kwargs):
        pass

    def render(self, request):
        raise Http404("Not Implemented")

    unique_name = None
    @classmethod
    def get_unique_name(cls):
        if not cls.unique_name:
            global unique_name_counter
            unique_name_counter += 1
            cls.unique_name = '{}-{}'.format(cls.__name__, unique_name_counter)

        return cls.unique_name

    @classmethod
    def url(cls, *args, **kwargs):
        return reverse(cls.get_unique_name(), args=args, kwargs=kwargs)

    @classmethod
    def amp_url(cls, *args, **kwargs):
        return reverse(cls.get_unique_name() + '.amp', args=args, kwargs=kwargs)

    @classmethod
    def sitemap(cls):
        return True

    @classmethod
    def get_sitemap(cls, include_false=False):
        sitemap = cls.sitemap()
        if sitemap == True or (sitemap == False and include_false):
            try:
                u = cls.url()
                return [[]]
            except NoReverseMatch:
                return []
        elif isinstance(sitemap, str):
            return [sitemap]
        elif isinstance(sitemap, list):
            return sitemap

        return []

    @classmethod
    def make_amp_route(cls, route):
        new = route[:-1] if route.endswith('$') else route
        if not len(new) or new[-1] in '^/':
            new += 'amp'
        else:
            new += '.amp'
        if route.endswith('$'):
            new += '$'
        return new


class NotFound404(Exception):
    pass


class BasePageHandler(BaseHandler):
    ignored_variables = ['items', 'modals', 'nav', 'container', 'base_object', 'current_user', 'user']

    def __init__(self, *args, **kwargs):
        self.title = ''
        self.description = ''
        self.keywords = ''
        self.author = ''
        self.robots_index = True
        self.robots_follow = True

        self.extra_css_files = []
        self.extra_js_files = []

        self.javascript = ''
        self.css = ''
        self.items = Collection()
        self.base_object = self.items
        self.modals = Collection()
        self.nav = None
        self.crumbs = []
        self.main = None
        self.footer = None

        self.identifier = None

        self.edit_mode = False

    def init(self):
        pass

    def output_html(self, start_time, init_time, render_time, args, kwargs):
        content = Collection()
        if self.nav:
            content.append(self.nav)
        if self.main:
            content.append(self.main)
        if self.crumbs:
            self.base_object.insert(0, Row(Div(BreadCrumbs(*self.crumbs), classes='col-md-12')))

        content.append(self.items)

        if self.footer:
            content.append(self.footer)

        keep_variables = {}
        for variable_name in dir(self):
            if variable_name not in self.ignored_variables:
                variable = self.__getattribute__(variable_name)
                if isinstance(variable, BaseObject):
                    keep_variables[variable_name] = variable.serialize()

        javascript = self.javascript
        css = self.css
        if self.modals:
            modals_html = self.modals.render(self, 8)
            javascript += '        ' + self.modals.render_js('        ')
            css += '            ' + self.modals.render_css('            ')
        else:
            modals_html = ''

        if content:
            content_html, content_css = content.render(self, 8)
            javascript += content.render_js('            ')
            css += '            ' + content.render_css('            ')
            css += ''.join(['\r\n            ' + line for line in content_css.splitlines()])
        else:
            content_html = ''

        if not javascript.strip():
            javascript = ''

        if not css.strip():
            css = ''

        # #TODO: Use the tornado mechanism for this?
        for resource in Resources.resources:
            if resource.type == 'css' and not resource.url in self.extra_css_files:
                self.extra_css_files.append(resource.url)
            elif resource.type == 'js' and not resource.url in self.extra_js_files:
                self.extra_js_files.append(resource.url)

        output_time = time.clock()
        content_html = content_html + '<!-- Init: {} Render: {} Output: {} -->'.format(init_time-start_time, render_time-init_time, output_time-render_time)

        html = render(self.request, 'base.html', {
                                  'title':self.title,
                                  'description':self.description.replace('"', '\''),
                                  'keywords':self.keywords,
                                  'author':self.author,
                                  'modals':modals_html,
                                  'content':content_html,
                                  'extra_css':'\n\r'.join(['        <link rel="stylesheet" href="' + css_file + '"/>' for css_file in self.extra_css_files]),
                                  'extra_js':'\n\r'.join(['        <script src="' + js_file + '"></script>' for js_file in self.extra_js_files]),
                                  'javascript':javascript,
                                  'css':css,
                                  'keep_variables':keep_variables,
                                  'amp_url':self.request.build_absolute_uri(self.amp_url(*args, **kwargs)) if self.enable_amp else None
        })

        return html

    def output_amp_html(self, args, kwargs):
        content = Collection()
        if self.nav:
            content.append(self.nav)
        if self.main:
            content.append(self.main)
        if self.crumbs:
            self.base_object.insert(0, Row(Div(BreadCrumbs(*self.crumbs), classes='col-md-12')))

        content.append(self.items)

        if self.footer:
            content.append(self.footer)

        if content:
            content_html, content_css = content.render_amp(self)
            css = '\r\n'.join(content_css.splitlines()) + '\r\n'
        else:
            content_html = ''
            css = ''

        html = render(self.request, 'base_amp.html', {
                                  'title':self.title,
                                  'description':self.description.replace('"', '\''),
                                  'keywords':self.keywords,
                                  'author':self.author,
                                  'full_url':self.request.build_absolute_uri(self.url(*args, **kwargs)),
                                  'content':content_html,
                                  'css':content_css
        })

        return html

    def render(self, request, *args, **kwargs):
        self.request = request
        self.shark_settings = request.shark_settings
        self.user = self.request.user

        if request.method == 'GET':
            self.edit_mode = self.user.is_superuser
            start_time = time.clock()
            self.init()
            if request.shark_settings.google_analytics_code:
                self.append(GoogleAnalyticsTracking(request.shark_settings.google_analytics_code))
            init_time = time.clock()
            try:
                self.render_page(*args, **kwargs)
            except NotFound404:
                output = Http404()
            else:
                render_time = time.clock()
                output = self.output_html(start_time, init_time, render_time, args, kwargs)
            return output
        elif request.method == 'POST':
            action = self.request.POST.get('action', '')
            keep_variables = json.loads(self.request.POST.get('keep_variables', '{}'))
            for variable_name in keep_variables:
                self.__setattr__(variable_name,
                                 PlaceholderWebObject(
                                     self,
                                     keep_variables[variable_name]['id'],
                                     keep_variables[variable_name]['class_name']
                                 )
                )
            self.html = ''
            self.javascript = ''
            self.data = {}
            arguments = {}
            for argument in self.request.POST:
                if argument == 'identifier':
                    self.__setattr__(argument, self.request.POST[argument])
                elif argument not in ['action', 'keep_variables', 'csrfmiddlewaretoken']:
                    arguments[argument] = self.request.POST[argument]

            if action:
                self.__getattribute__(action)(*args, **arguments)

            self.html += self.items.render('')
            self.javascript += self.items.render_js('')
            data = {'javascript': self.javascript,
                    'html': self.html,
                    'data': self.data}
            json_data = json.dumps(data)

            return HttpResponse(json_data)

    def render_amp(self, request, *args, **kwargs):
        self.request = request
        self.user = self.request.user

        if request.method == 'GET':
            self.init()
            try:
                self.render_amp_page(*args, **kwargs)
            except NotFound404:
                output = Http404()
            else:
                output = self.output_amp_html(args, kwargs)
            return output

        return HttpResponse('AMP Page')

    def append(self, *items):
        self.base_object.append(*items)
        if items:
            return items[0]
        else:
            return None

    def append_row(self, *args, **kwargs):
        self.append(Row(Div(args, classes='col-md-12'), **kwargs))

    def add_javascript(self, script):
        self.javascript = self.javascript + script

    def render_page(self):
        raise NotImplementedError

    def render_amp_page(self, *args, **kwargs):
        return self.render_page(*args, **kwargs)

    def text(self, name, default_txt=None):
        text = EditableText.load(name)
        if not text:
            text = EditableText()
            text.name = name
            text.content = default_txt or name
            text.filename = ''
            text.handler_name = self.__class__.__name__
            text.line_nr = 0
            text.last_used = now()
            text.save()

        return text.content

    def _save_term(self, name, content):
        if self.user.is_superuser:
            text = EditableText.load(name)
            text.content = content
            text.save()


def exists_or_404(value):
    if not value:
        raise Http404()
    return value


Resources.add_resource('http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css', 'css', 'bootstrap', 'main')


class HandlerTestCase(TestCase):
    def setUp(self):
        pass

    url = None
    def test_response_is_200(self):
        if self.__class__.url:
            print('URL', self.__class__.url)
            client = Client()
            response = client.get(self.__class__.url)

            self.assertEqual(response.status_code, 200)


class Container(BaseObject):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the container', Collection())
        self.add_class('container')

    def get_html(self, html):
        html.append('<div' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</div>')

    def get_amp_html(self, html):
        html.append('<div' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</div>')

    def insert(self, i, x):
        self.items.insert(i, x)


class BaseContainerPageHandler(BasePageHandler):
    def __init__(self, *args, **kwargs):
        super(BaseContainerPageHandler, self).__init__(*args, **kwargs)

        self.container = Container()
        self.items.append(self.container)
        self.base_object = self.container


def listify(obj):
    if not isinstance(obj, (list, set)):
        return [obj]
    else:
        return obj


def shark_django_handler(request, *args, handler=None, settings=None, **kwargs):
    handler_instance = handler()
    request.shark_settings = settings
    outcome = handler_instance.render(request, *args, **kwargs)
    return outcome


def shark_django_amp_handler(request, *args, handler=None, settings=None, **kwargs):
    handler_instance = handler()
    request.shark_settings = settings
    outcome = handler_instance.render_amp(request, *args, **kwargs)
    return outcome


class StaticPage(BasePageHandler):
    def render_page(self, url_name):
        page = StaticPageModel.load(url_name)
        if not page:
            raise NotFound404()

        self.title = page.title
        self.description = page.description
        self.append(Markdown(page.body))

    @classmethod
    def url(cls, *args, **kwargs):
        return reverse('shark_static_page', args=args, kwargs=kwargs)

    @classmethod
    def amp_url(cls, *args, **kwargs):
        return reverse('shark_static_page.amp', args=args, kwargs=kwargs)

    @classmethod
    def sitemap(cls):
        pages = models.StaticPage.objects.filter(sitemap=True).all()
        return [sp.url_name for sp in pages]


def markdown_preview(request):
    """ Render preview page.
    :returns: A rendered preview
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_staff:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    dirty = markdown.markdown(text=escape(request.POST.get('data', 'No content posted')), output_format='html5')
    value = bleach.clean(dirty, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES)
    return HttpResponse(value)


class SiteMap(BaseHandler):
    route = '^sitemap.xml$'

    def get_urls(self, include_false=False):
        urls = set()

        handlers = set()
        for pattern in get_resolver().url_patterns:
            if isinstance(pattern, RegexURLResolver):
                pass
            elif isinstance(pattern, RegexURLPattern):
                if 'handler' in pattern.default_args and issubclass(pattern.default_args['handler'], BaseHandler):
                    handler = pattern.default_args['handler']
                    if handler not in handlers:
                        handlers.add(handler)
                        for args in handler.get_sitemap(include_false):
                            if isinstance(args, str) or not isinstance(args, Iterable):
                                args=[args]
                            urls.add(handler.url(*args))
                            if handler.enable_amp:
                                urls.add(handler.amp_url(*args))

        return urls

    def render(self, request):
        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        handlers = set()
        for url in self.get_urls():
            lines.append('    <url><loc>{}</loc></url>'.format(request.build_absolute_uri(url)))

        lines.append('</urlset>')
        return HttpResponse('\r\n'.join(lines))

    @classmethod
    def sitemap(cls):
        return False


class Favicon(BaseHandler):
    route = '^favicon.ico$'

    def render(self, request):
        return serve(request, 'favicon.ico', 'static/icons')

class GoogleVerification(BaseHandler):
    def render(self, request):
        return HttpResponse('google-site-verification: {}.html'.format(request.shark_settings.google_verification))

    @classmethod
    def sitemap(cls):
        return False


class BingVerification(BaseHandler):
    route = '^BingSiteAuth.xml$'

    def render(self, request):
        return HttpResponse('<?xml version="1.0"?><users><user>{}</user></users>'.format(request.shark_settings.bing_verification))

    @classmethod
    def sitemap(cls):
        return False


class YandexVerification(BaseHandler):
    def render(self, request):
        return HttpResponse('<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>Verification: {}</body></html>'.format(request.shark_settings.yandex_verification))

    @classmethod
    def sitemap(cls):
        return False


class SharkSettings:
    def __init__(self):
        self.modules = []
        self.page_handler = None
        self.use_static_pages = True
        self.static_amp = False
        self.google_analytics_code = None
        self.google_verification = None
        self.bing_verification = None
        self.yandex_verification = None

    def urls(self):
        handlers = []
        def add_handler(obj, route=None):
            if inspect.isclass(obj) and issubclass(obj, BaseHandler) and 'route' in dir(obj):
                if route or obj.route:
                    if obj.enable_amp:
                        handlers.append(url(obj.make_amp_route(route or obj.route), shark_django_amp_handler, {'handler': obj, 'settings': self}, name=obj.get_unique_name() + '.amp'))
                    handlers.append(url(route or obj.route, shark_django_handler, {'handler': obj, 'settings': self}, name=obj.get_unique_name()))

        for mod in listify(self.modules):
            if inspect.ismodule(mod):
                objs = [getattr(mod, key) for key in dir(mod)]
            else:
                objs = mod

            for obj in objs:
                add_handler(obj)

        add_handler(SiteMap)

        if self.page_handler and self.use_static_pages:
            StaticPage.enable_amp = self.static_amp
            if StaticPage.enable_amp:
                handlers.append(url(
                        '^page/(.*).amp$',
                        shark_django_amp_handler,
                        {'handler': new_class('StaticPage', (StaticPage, self.page_handler)), 'settings': self},
                        name='shark_static_page.amp'
                ))
            handlers.append(url(
                    '^page/(.*)$',
                    shark_django_handler,
                    {'handler': new_class('StaticPage', (StaticPage, self.page_handler)), 'settings': self},
                    name='shark_static_page'
            ))

        handlers.append(url(r'^markdown_preview/$', markdown_preview, name='django_markdown_preview'))

        if self.google_verification:
            add_handler(GoogleVerification, '^{}.html$'.format(self.google_verification))

        if self.bing_verification:
            add_handler(BingVerification, '^BingSiteAuth.xml$')

        if self.yandex_verification:
            add_handler(YandexVerification, '^yandex_{}.html$'.format(self.yandex_verification))

        return handlers
