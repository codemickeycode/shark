import json

from django.utils.html import escape
from django.utils.http import urlquote


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if 'serializable_object' in dir(o):
            return o.serializable_object()

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)


def js_action(action, **kwargs):
    json_params = ExtendedJSONEncoder().encode(kwargs)
    return u'do_action(\'' + escape(action) + '\', ' + escape(json_params) + u');return false;'


class BaseAction:
    """
    In websites there are many places where actions happen, such as:
    - Anchors have URLs
    - Forms get submitted
    - Buttons get clicked
    - CloseIcon gets clicked
    Different outcomes are required, and they fall in 3 groups:
    - Open a URL
    - Execute some Javascript
    - Execute a server-side action
    Anywhere in Shark where you can open a URL (Like Anchor of NavLink, etc) or some JS, you can use any type of action.
    """
    @property
    def url(self):
        """
        Places that have anchors &lt;a&gt;, can use this to get the URL
        :return: Plain URL
        """
        return ''

    @property
    def js(self):
        """
        This will return the Javascript version of any action, including URLs
        :return: Full javascript for any action
        """
        return ''

    @property
    def href(self):
        """
        Attribute to add to an HTML element that supports href. But for javascript actions we use onclick
        """
        if self.url:
            return ' href="{}"'.format(self.url)
        elif self.js:
            return ' onclick="{}"'.format(self.js)
        return ''

    @property
    def onclick(self):
        """
        Attribute to add to an HTML element that doesn't support href. onclick is used
        """
        return ' onclick="{}"'.format(self.js)


class URL(BaseAction):
    def __init__(self, url):
        self._url = urlquote(url) if url else ''

    @property
    def url(self):
        return self._url

    @property
    def js(self):
        if not self._url:
            return ''

        return 'window.location.href="{}";'.format(self._url)

    def __repr__(self):
        return self._url

    def __str__(self):
        return self._url


class JS(BaseAction):
    def __init__(self, js):
        self._js = js

    @property
    def js(self):
        return self._js


class Action(BaseAction):
    def __init__(self, action, **kwargs):
        self._action = action
        self.kwargs = kwargs

    @property
    def js(self):
        return 'do_action("{}", {});'.format(self._action, json.dumps(self.kwargs))


class NoAction(BaseAction):
    pass


class JQ(object):
    def __init__(self, js, obj=None):
        self.js = js
        self.obj = obj

    def show(self):
        return JQ(self.js + '.show()', self.obj)

    def hide(self):
        return JQ(self.js + '.hide()', self.obj)

    def fadeIn(self):
        return JQ(self.js + '.fadeIn()', self.obj)

    def fadeOut(self):
        return JQ(self.js + '.fadeOut()', self.obj)


