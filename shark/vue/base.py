import inspect
import json

from django.utils.http import urlquote
from shark.actions import JS
from shark.base import Object, Value, Objects
from shark.param_converters import ObjectsParam, ListParam


class Data(Value):
    def __init__(self, vue, name, data):
        self.vue = vue
        self.name = name
        self.data = data

    def __getattr__(self, item):
        return '{{' + self.name + '.' + item + '}}'

    def as_param(self):
        return '{{' + self.name + '}}'

    def as_attr(self, name):
        return 'v-bind:' + name + "='" + urlquote(str(self)) + "'"

    def set(self, value):
        return JS('{}{}={}'.format(self.vue.id + '.' if self.vue else '', self.name, json.dumps(value)))


class VueData(object):
    def __init__(self, vue, **kwargs):
        self._vue = vue
        self._data = {}
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def __setattr__(self, key, value):
        if key in ['_vue', '_data']:
            super().__setattr__(key, value)
        else:
            self._data[key] = Data(self._vue, key, value)

    def __getattr__(self, item):
        return self._data[item]

    def _render(self):
        return '{' + ','.join(['"{}": {}'.format(key, json.dumps(value.data)) for key, value in self._data.items()]) + '}'


class Component(Object):
    # Don't create this directly, use the component decorator on a function instead
    def __init__(self, props, items, **kwargs):
        self.init(kwargs)
        self.props = self.param(props, ListParam, 'Properties')
        self.items = self.param(items, ObjectsParam, 'The template')

        self.rendered = False

    def get_html(self, renderer):
        if not self.rendered:
            html, js = renderer.render_string_and_js(self.items)
            # TODO: What about js?
            props = ','.join(["'{}'".format(prop) for prop in self.props])
            renderer.append_js("Vue.component('{}', {{props:[{}], template:{}}});".format(self.id, props, json.dumps(html)))
            self.rendered = True


class ComponentUse(Object):
    def __init__(self, obj=None, args=None, **kwargs):
        self.init(kwargs)
        self.obj = self.param(obj, Component, 'Vue Component')
        self.args = self.param(args, ListParam, 'Argument names passed in')

    def get_html(self, renderer):
        renderer.render('', self.obj)
        bindings = ''.join([' :{}="{}"'.format(prop, arg) for prop, arg in zip(self.obj.props, self.args)])
        renderer.append('<{}{}></{}>'.format(self.obj.id, bindings, self.obj.id))


def component(func):
    params = list(inspect.signature(func).parameters.keys())
    func_args = [Data(None, param, None) for param in params]
    obj = Component(params, func(*func_args))

    def wrapper(*args, **kwargs):
        return ComponentUse(obj, [arg.name for arg in args])

    return wrapper


class Vue(Object):
    def __init__(self, **kwargs):
        self.init(kwargs)
        self.id_needed()
        self.items = Objects()
        self.data = VueData(self, **kwargs)

    def __call__(self, *args, **kwargs):
        self += args
        return self

    def get_html(self, renderer):
        renderer.add_resource('https://unpkg.com/vue/dist/vue.js', 'js', 'vue', 'main')

        renderer.append('<div' + self.base_attributes + '>')
        renderer.render('    ', self.items)
        renderer.append('</div>')

        renderer.append_js("var {} = new Vue({{el:'#{}', data:{}}});".format(self.id, self.id, self.data._render()))
