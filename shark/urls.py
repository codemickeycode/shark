import inspect
from types import new_class
from logging import handlers

from django.conf.urls import url

from django.conf import settings
from shark.handler import markdown_preview, BaseHandler, shark_django_handler, shark_django_amp_handler, StaticPage, \
    SiteMap, GoogleVerification, BingVerification, YandexVerification
from shark.settings import SharkSettings


def get_urls():
    urlpatterns = []

    def add_handler(obj, route=None):
        if inspect.isclass(obj) and issubclass(obj, BaseHandler) and 'route' in dir(obj):
            if route or obj.route:
                if obj.enable_amp:
                    urlpatterns.append(url(obj.make_amp_route(route or obj.route), shark_django_amp_handler, {'handler': obj}, name=obj.get_unique_name() + '.amp'))
                urlpatterns.append(url(route or obj.route, shark_django_handler, {'handler': obj}, name=obj.get_unique_name()))

    apps = settings.INSTALLED_APPS
    for app_name in apps:
        try:
            app = __import__(app_name + '.views').views
        except ImportError:
            pass
        else:
            objs = [getattr(app, key) for key in dir(app)]

            for obj in objs:
                add_handler(obj)

    if SharkSettings.SHARK_PAGE_HANDLER and SharkSettings.SHARK_USE_STATIC_PAGES:
        handler_parts = SharkSettings.SHARK_PAGE_HANDLER.split('.')
        obj = __import__(handler_parts[0])
        for handler_part in handler_parts[1:]:
            obj = obj.__dict__[handler_part]

        StaticPage.enable_amp = SharkSettings.SHARK_STATIC_AMP
        if StaticPage.enable_amp:
            urlpatterns.append(url(
                    '^page/(.*).amp$',
                    shark_django_amp_handler,
                    {'handler': new_class('StaticPage', (StaticPage, obj))},
                    name='shark_static_page.amp'
            ))

        urlpatterns.append(url(
                '^page/(.*)$',
                shark_django_handler,
                {'handler': new_class('StaticPage', (StaticPage, obj))},
                name='shark_static_page'
        ))

    urlpatterns.append(url(r'^markdown_preview/$', markdown_preview, name='django_markdown_preview'))

    add_handler(SiteMap)

    if SharkSettings.SHARK_GOOGLE_VERIFICATION:
        add_handler(GoogleVerification, '^{}.html$'.format(SharkSettings.SHARK_GOOGLE_VERIFICATION))

    if SharkSettings.SHARK_BING_VERIFICATION:
        add_handler(BingVerification, '^BingSiteAuth.xml$')

    if SharkSettings.SHARK_YANDEX_VERIFICATION:
        add_handler(YandexVerification, '^yandex_{}.html$'.format(SharkSettings.SHARK_YANDEX_VERIFICATION))

    return urlpatterns
