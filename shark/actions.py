import json
from inspect import ismethod

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
            return ' onclick="{}"'.format(self.js.replace('"', '&quot;'))
        return ''

    @property
    def onclick(self):
        """
        Attribute to add to an HTML element that doesn't support href. onclick is used
        """
        return ' onclick="{}"'.format(self.js.replace('"', '&quot;'))


class URL(BaseAction):
    def __init__(self, url, quote=True):
        if url:
            if quote:
                self._url = urlquote(url, ':/@')
            else:
                self._url = url
        else:
            self._url = ''

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
    def __init__(self, obj_js, obj=None, renderer=None):
        self._js_pre = ''
        self._js_post = ''
        self.obj_js = obj_js
        self.obj = obj
        self.renderer = renderer

    def __getattr__(self, item):
        if self.obj:
            func = self.obj.__getattribute__(item)
            if ismethod(func):
                return lambda *args, **kwargs: self + func(*args, **kwargs)

        raise KeyError(item)

    def __add__(self, other):
        if isinstance(other, JQ):
            other._js_pre = self._js_pre + other._js_pre
            other._js_post = self._js_post + other._js_post
            return other
        elif isinstance(other, str):
            self._js_pre += other
            return self
        elif not other:
            return self
        else:
            raise TypeError('Cannot concatenate JQ object {} with {}'.format(self, other.__class__.__name__))

    def show(self):
        self._js_pre += '{}.show();'.format(self.obj_js)
        return self

    def hide(self):
        self._js_pre += '{}.hide();'.format(self.obj_js)
        return self

    def fadeIn(self):
        self._js_pre += '{}.fadeIn(400, function(){{'.format(self.obj_js)
        self._js_post += '});'
        return self

    def fadeOut(self):
        self._js_pre += '{}.fadeOut(400, function(){{'.format(self.obj_js)
        self._js_post += '});'
        return self

    def animate(self, **kwargs):
        self._js_pre += '{}.animate({}, function(){{'.format(self.obj_js, json.dumps(kwargs))
        self._js_post += '});'
        return self

    def attr(self, attr, value):
        self._js_pre += '{}.attr("{}", {});'.format(self.obj_js, attr, json.dumps(value))
        return self

    def html(self, content):
        if self.obj:
            variable = self.obj.add_variable(content)
        elif self.renderer:
            variable = self.renderer.add_variable(content)
        else:
            raise NotImplementedError('Nowhere to store the variable')

        self._js_pre += '{}.html({});func_{}();'.format(self.obj_js, variable, variable)
        return self

    def append_raw(self, content):
        self._js_pre += '{}.append({});'.format(self.obj_js, json.dumps(content))
        return self

    def replace_resource(self, resource):
        id = "#resource-{}-{}".format(resource.resource.module, resource.name)
        self._js_pre += '$("#{}").remove();'.format('id')
        self._js_pre += '$("head").append("<link id=\'{}\' rel=\'stylesheet\' href=\'{}\' type=\'text/css\' />");'.format(id, resource.url)
        return self

    @property
    def js(self):
        return self._js_pre + self._js_post