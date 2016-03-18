import inspect
from types import new_class
from logging import handlers

from django.conf.urls import url

from django.conf import settings

from shark.common import listify
from shark.handler import markdown_preview, BaseHandler, shark_django_handler, shark_django_amp_handler, StaticPage, \
    SiteMap, GoogleVerification, BingVerification, YandexVerification, shark_django_redirect_handler
from shark.settings import SharkSettings


def get_urls():
    urlpatterns = []
    redirects = []

    def add_handler(obj, route=None):
        if inspect.isclass(obj) and issubclass(obj, BaseHandler) and 'route' in dir(obj):
            if route or obj.route:
                if obj.enable_amp:
                    urlpatterns.append(url(obj.make_amp_route(route or obj.route), shark_django_amp_handler, {'handler': obj}, name=obj.get_unique_name() + '.amp'))
                urlpatterns.append(url(route or obj.route, shark_django_handler, {'handler': obj}, name=obj.get_unique_name()))

            for redirect_route in listify(obj.redirects):
                if isinstance(redirect_route, str):
                    redirects.append(url(redirect_route, shark_django_redirect_handler, {'handler': obj}))
                elif isinstance(redirect_route, tuple):
                    for redirect_sub_route in redirect_route[0]:
                        redirects.append(url(redirect_sub_route, shark_django_redirect_handler, {'handler': obj, 'function':redirect_route[1]}))


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

    if SharkSettings.SHARK_GOOGLE_VERIFICATION:
        add_handler(GoogleVerification, '^{}.html$'.format(SharkSettings.SHARK_GOOGLE_VERIFICATION))

    if SharkSettings.SHARK_BING_VERIFICATION:
        add_handler(BingVerification, '^BingSiteAuth.xml$')

    if SharkSettings.SHARK_YANDEX_VERIFICATION:
        add_handler(YandexVerification, '^yandex_{}.html$'.format(SharkSettings.SHARK_YANDEX_VERIFICATION))

    urlpatterns.extend(redirects)
    return urlpatterns
