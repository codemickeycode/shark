import json
from inspect import ismethod

from shark.base import Object
from shark.dependancies import escape_html, escape_url


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if 'serializable_object' in dir(o):
            return o.serializable_object()

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)


def js_action(action, **kwargs):
    json_params = ExtendedJSONEncoder().encode(kwargs)
    return 'do_action(\'' + escape_html(action) + '\', ' + escape_html(json_params) + ');return false;'


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
    def url(self, renderer):
        """
        Places that have anchors &lt;a&gt;, can use this to get the URL
        :return: Plain URL
        """
        return ''

    def js(self, renderer):
        """
        This will return the Javascript version of any action, including URLs
        :return: Full javascript for any action
        """
        return ''

    def href(self, renderer):
        """
        Attribute to add to an HTML element that supports href. But for javascript actions we use onclick
        """
        url = self.url(renderer)
        js = self.js(renderer)
        if url:
            return ' href="{}"'.format(url)
        elif js:
            # TODO: Use a proper escape function?
            return ' onclick="{}"'.format(js.replace('"', '&quot;'))
        return ''

    def onclick(self, renderer):
        """
        Attribute to add to an HTML element that doesn't support href. onclick is used
        """
        #TODO: Use a proper escape function?
        js = self.js(renderer)
        return ' onclick="{}"'.format(js.replace('"', '&quot;'))


class URL(BaseAction):
    def __init__(self, url, quote=True):
        if url:
            if quote:
                self._url = escape_url(url)
            else:
                self._url = url
        else:
            self._url = ''

    def url(self, renderer):
        return self._url

    def js(self, renderer):
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

    def js(self, renderer):
        return self._js

    def __repr__(self):
        return self._js

    def __str__(self):
        return self._js


class Action(BaseAction):
    def __init__(self, action, **kwargs):
        self._action = action
        self.kwargs = kwargs

    def js(self, renderer):
        return 'do_action("{}", {});'.format(self._action, json.dumps(self.kwargs))

    def __repr__(self):
        return 'Action("{}")'.format(self._action)

    def __str__(self):
        return 'Action("{}")'.format(self._action)


class NoAction(BaseAction):
    def __bool__(self):
        return False


class JQ(BaseAction, Object):
    def __init__(self, obj_js, obj=None):
        self._js_pre = ''
        self._js_post = ''
        self.obj_js = obj_js
        self.obj = obj
        self._rendered_js = None
        self.init({})

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
        elif isinstance(other, BaseAction):
            self._js_post += other.js
            return self
        elif isinstance(other, str):
            self._js_post += other
            return self
        elif not other:
            return self
        else:
            raise TypeError('Cannot concatenate JQ object {} with {}'.format(self, other.__class__.__name__))

    def __radd__(self, other):
        if isinstance(other, BaseAction):
            self._js_pre = other.js + self._js_pre
            return self
        elif isinstance(other, str):
            self._js_pre = other + self._js_pre
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

    def val(self, value):
        self._js_pre += '{}.val({});'.format(self.obj_js, json.dumps(value))
        return self

    def html(self, content):
        variable = self.add_variable(content)
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

    def js(self, renderer):
        if self._rendered_js is None:
            renderer.render_variables(self._variables)
            self._rendered_js = self._js_pre + self._js_post

        return self._rendered_js

    def get_html(self, renderer):
        renderer.append_js(self.js(renderer))


def jq_by_id(id):
    return JQ('$("#{}")'.format(id))
