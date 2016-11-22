import inspect
import json
import logging
import re
from collections import Iterable
from functools import partial

import bleach
from django.utils.html import escape
from django.utils.http import urlquote
from markdown import markdown

from shark.actions import URL, NoAction, BaseAction, JS, Action, JQ
from shark.resources import Resources
from .common import LOREM_IPSUM

Default = object()
NotProvided = object()

class Enumeration(object):
    _value_map = None

    @classmethod
    def value_map(cls):
        obj = cls()
        if not cls._value_map:
            cls._value_map = {obj.__getattribute__(name):name for name in dir(cls) if name not in dir(Enumeration) and isinstance(obj.__getattribute__(name), int)}

        return cls._value_map

    @classmethod
    def name(cls, value):
        return cls.value_map()[value]

    @classmethod
    def names(cls):
        return cls.value_map().values()


ALLOWED_TAGS = ['ul', 'ol', 'li', 'p', 'pre', 'code', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'br', 'strong', 'em', 'a', 'img', 'div', 'span']

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'title', 'alt'],
    'div': ['style'],
    'span': ['style']
}

ALLOWED_STYLES = ['color', 'font-weight']


class BaseObject(object):
    object_number = 0

    def init(self, kwargs):
        self.id = kwargs.pop('id', None)
        self.classes = kwargs.pop('classes', '')
        self.style = kwargs.pop('style', '')
        self.extra_attributes = ''
        self.parent = None

        self.variables = {}

        for kwarg in ['id', 'style', 'tab_index', 'role', 'onclick']:
            kwargs.pop(kwarg, None)

    def id_needed(self):
        if not self.id:
            self.__class__.object_number += 1
            self.obj_nr = self.__class__.object_number
            self.id = '%s_%s' % (self.__class__.__name__, self.obj_nr)

    def param(self, value, type, description='', default=None):
        if value == Default:
            value = default
            if value == Default:
                return Default

        if type == 'string':
            if not value is None:
                if not isinstance(value, str):
                    value = str(value)
                value = escape(value)
            else:
                value = ''
        elif type == 'raw':
            if not value is None:
                if isinstance(value, Raw):
                    value = value.text
            else:
                value = ''
        elif type == 'url':
            if isinstance(value, str):
                value = urlquote(value, ':/@')
            elif isinstance(value, URL):
                value = value.url
            elif not value:
                value = ''
            else:
                value = urlquote(str(value, ':/@'))
        elif type == 'URL':
            if not value:
                value = NoAction()
            elif isinstance(value, str):
                value = URL(value)
            elif isinstance(value, JQ):
                value = JS(value.js)
            elif not isinstance(value, BaseAction):
                raise TypeError('Value is not a valid type for a URL')
        elif type == 'JS':
            if not value:
                value = NoAction()
            elif isinstance(value, str):
                value = JS(value)
            elif isinstance(value, JQ):
                value = JS(value.js)
            elif not isinstance(value, BaseAction):
                logging.warning('Value is not a BaseAction or str.')
                value = None
        elif type == 'Action':
            if not value:
                value = NoAction()
            elif isinstance(value, str):
                value = Action(value)
            elif isinstance(value, JQ):
                value = JS(value.js)
            elif not isinstance(value, BaseAction):
                logging.warning('Value is not a BaseAction or str.')
                value = None

        elif type == 'markdown':
            if isinstance(value, Raw):
                value = value.text
            value = Markdown(value)
        elif type == 'int':
            if value is not None:
                value = int(value)
        elif type == 'Collection':
            if value is None:
                value = Collection()
            elif isinstance(value, Collection):
                pass
            elif isinstance(value, BaseObject):
                value = Collection([value])
            elif isinstance(value, str):
                value = Collection([Text(value)])
            elif isinstance(value, int):
                value = Collection([Text(str(value))])
            elif isinstance(value, Iterable):
                value = Collection(value)
            elif 'parent' not in dir(value) or 'render' not in dir(value):
                raise TypeError('Class {} was passed {} of type {} but expected a Collection, list, Object, string or int.'.format(self.__class__.__name__, value, value.__class__.__name__))
            value.parent = self
        elif type == 'list':
            if not value.__class__ is list:
                value = [value]

        return value

    def append(self, *args, **kwargs):
        if 'items' in dir(self):
            self.__getattribute__('items').append(*args, **kwargs)
        else:
            raise KeyError('Object has no "items" Collection. Are you trying to self.append in the get_html of a Shark Object? Use the renderer instead.')

    @property
    def base_attributes(self):
        attributes = []
        if self.id:
            attributes.append(' id="' + self.id + '"')
        if self.classes:
            attributes.append(' class="' + self.classes + '"')
        if self.style:
            attributes.append(' style="' + self.style + '"')
        attributes.append(self.extra_attributes)

        return ''.join(attributes)

    def add_class(self, class_names):
        new_classes = class_names.split()
        existing_classes = self.classes.split()
        for class_name in new_classes:
            if class_name not in existing_classes:
                self.classes = (self.classes + ' ' + class_name)

        self.classes = self.classes.strip()

    def add_attribute(self, attribute, value):
        if value is not None:
            self.extra_attributes = (self.extra_attributes + ' ' + attribute + '="' + escape(str(value)) + '"')
        else:
            self.extra_attributes = (self.extra_attributes + ' ' + attribute)


    def render(self, handler=None, indent=0):
        html = Renderer(handler=handler, indent=indent)
        try:
            self.get_html(html)
        except AttributeError as e:
            print(self)
            raise e

        return html.output()

    def get_html(self, renderer):
        pass

    def serialize(self):
        return {'class_name': self.__class__.__name__, 'id': self.id}

    def __add__(self, other):
        obj = objectify(other)
        if not obj:
            return self
        elif isinstance(obj, BaseObject):
            return Collection([self, obj])
        elif isinstance(obj, Collection):
            obj.insert(0, self)
            return obj

    def __iadd__(self, other):
        obj = objectify(other)
        if not obj:
            return self
        elif isinstance(obj, BaseObject):
            return Collection([self, obj])
        elif isinstance(obj, Collection):
            obj.insert(0, self)
            return obj

    def replace_with(self, new_object):
        pass # For code completion

    @property
    def jq(self):
        self.id_needed()
        return JQ("$('#{}')".format(self.id), self)

    @classmethod
    def example(cls):
        return None


def objectify(obj):
    if isinstance(obj, (BaseObject, Collection)):
        return obj
    elif not obj:
        return None
    elif isinstance(obj, str):
        return Text(obj)
    elif isinstance(obj, Iterable):
        return Collection(*obj)
    else:
        raise TypeError('Cannot cast to Shark Object')


class PlaceholderWebObject(object):
    def __init__(self, handler, id, class_name):
        self.handler = handler
        self.id = id
        self.class_name = class_name
        self.variables = {}
        self.jqs = []

    @property
    def jq(self):
        jq = JQ("$('#{}')".format(self.id), self)
        self.jqs.append(jq)
        return jq

    def add_variable(self, web_object):
        name = self.id.lower() + '_' + str(len(self.variables) + 1)
        self.variables[name] = objectify(web_object)
        return name

    #TODO: Support calling methods on the original class, like Image().src()
    def src(self, src):
        return self.jq.attr('src', src)



class Renderer:
    object_number = 0

    def __init__(self, handler=None, inline_style_class_base='style_'):
        self.__class__.object_number += 1
        self.id = self.__class__.__name__ + '_' + str(self.__class__.object_number)
        self._html = []
        self._rendering_to = self._html
        self._css = []
        self._css_classes = {}
        self._js = []
        self._rendering_js_to = self._js
        self.indent = 0
        self.handler = handler
        self.translate_inline_styles_to_classes = True
        self.inline_style_class_base = inline_style_class_base
        self.resources = Resources()
        self.parents = []
        self.variables = {}

        if handler:
            self.text = handler.text
        else:
            self.text = ''

        self.separator = '\r\n'
        self.omit_next_indent = False

        self.render_count = 0

    def add_css_class(self, css):
        if not css in self._css_classes:
            self._css_classes[css] = '{}{}'.format(self.inline_style_class_base, len(self._css_classes))
        return self._css_classes[css]

    def append(self, p_object):
        if isinstance(p_object, str):
            self._rendering_to.append((' '*self.indent if not self.omit_next_indent else '') + p_object + self.separator)
            self.omit_next_indent = False

    def append_css(self, css):
        self._css.append(css.strip())

    def append_js(self, js):
        js = js.strip()
        if not js.endswith(';'):
            js += ';'
        self._rendering_js_to.append(js)

    def add_variable(self, web_object):
        name = self.id.lower() + '_' + str(len(self.variables) + 1)
        self.variables[name] = objectify(web_object)
        return name

    def render_variables(self, variables):
        while variables:
            name, obj = variables.popitem()
            html, js = self.render_string_and_js(obj)
            self.append_js('var {} = {};'.format(name, json.dumps(html)))
            self.append_js('function func_{}(){{{}}};'.format(name, js))

    def render(self, indent, web_object):
        self.render_count += 1
        # self.render_variables(self.variables)

        if web_object:
            self.indent += len(indent)

            if self.translate_inline_styles_to_classes and isinstance(web_object, BaseObject) and web_object.style:
                web_object.add_class(self.add_css_class(web_object.style))
                web_object.style = ''

            if web_object.parent and isinstance(web_object.parent, BaseObject):
                self.parents.insert(0, web_object.parent)
                web_object.get_html(self)
                self.parents.pop(0)
            else:
                web_object.get_html(self)

            self.indent -= len(indent)

    def render_all(self, data):
        self.render('', objectify(data))

    def inline_render(self, web_object):
        if self.separator and len(self._rendering_to) and self._rendering_to[-1].endswith(self.separator):
            self._rendering_to[-1] = self._rendering_to[-1][:-len(self.separator)]
        if web_object:
            if not isinstance(web_object, BaseObject) and not isinstance(web_object, Collection):
                web_object = Collection(web_object)

            old_separator = self.separator
            self.separator = ''
            old_indent = self.indent
            self.indent = 0
            web_object.get_html(self)
            self.indent = old_indent

            self.separator = old_separator

        self.omit_next_indent = True

    def render_string(self, web_object):
        original = self._rendering_to
        self._rendering_to = []
        self.render('', web_object)
        html = self.html
        self._rendering_to = original
        return html

    def render_string_and_js(self, web_object):
        original = self._rendering_to
        original_js = self._rendering_js_to
        self._rendering_to = []
        self._rendering_js_to = []
        self.render('', web_object)
        html = self.html
        js = self.js
        self._rendering_to = original
        self._rendering_js_to = original_js
        return html, js

    def find_parent(self, type):
        for parent in self.parents:
            if isinstance(parent, type):
                return parent
        return None

    def add_resource(self, url, type, module, name=''):
        self.resources.add_resource(url, type, module, name)

    def replace_resource(self, url, type, module, name=''):
        self.resources.replace_resource(url, type, module, name)

    @property
    def html(self):
        return ''.join(self._rendering_to)

    @property
    def css(self):
        css = self._css.copy()
        for style, class_name in self._css_classes.items():
            css.append('.' + class_name + '{' + style + '}')

        return '\r\n'.join(css)

    @property
    def js(self):
        return '\r\n'.join(self._rendering_js_to)

    @property
    def css_files(self):
        return [resource.url for resource in self.resources.resources if resource.type=='css']

    @property
    def css_resources(self):
        return [resource for resource in self.resources.resources if resource.type=='css']

    @property
    def js_files(self):
        return [resource.url for resource in self.resources.resources if resource.type=='js']

    @property
    def js_resources(self):
        return [resource for resource in self.resources.resources if resource.type=='js']


class Collection(list):
    def __init__(self, *args, **kwargs):
        if len(args)>1:
            args = [args]
        elif len(args)==1:
            args = args[0]

        fixed_args = []
        for arg in args:
            if isinstance(arg, (BaseObject, Collection)):
                pass
            elif not arg:
                arg = None
            elif isinstance(arg, str):
                arg = Text(arg)
            elif isinstance(arg, Iterable):
                arg = Collection(arg)
            else:
                arg = Text(str(arg))

            fixed_args.append(arg)

        super(Collection, self).__init__(fixed_args, **kwargs)

        self.parent = None


    def append(self, *objects):
        for obj in objects:
            if obj:
                if isinstance(obj, str):
                    obj = Text(obj)
                if isinstance(obj, Iterable):
                    obj = Collection(obj)

                super(Collection, self).append(obj)
                obj.parent = self

    def get_html(self, html):
        if self.parent and isinstance(self.parent, BaseObject):
            html.parents.insert(0, self.parent)
        for web_object in self:
            html.render('', web_object)

        if self.parent and isinstance(self.parent, BaseObject):
            html.parents.pop(0)

    def render(self, handler=None):
        renderer = Renderer(handler=handler)
        self.get_html(renderer)

        return renderer

    def __add__(self, other):
        obj = objectify(other)
        if not obj:
            return self
        else:
            return Collection(self, obj)

    def __iadd__(self, other):
        obj = objectify(other)
        if not obj:
            return self
        else:
            return Collection(self, obj)


class Raw(BaseObject):
    """
    Raw html to be rendered. This text will not be escaped.
    Be careful with using this as it can lead to security issues.
    """
    def __init__(self, text=u'', **kwargs):
        self.init(kwargs)
        self.text = self.param(text, 'raw', 'Raw text')

    def get_html(self, html):
        html.append(self.text)

    def __str__(self):
        return self.text or ''

    @classmethod
    def example(self):
        return Raw('<b>Hello world!</b>')


class Text(BaseObject):
    """
    Just plain text.
    """
    def __init__(self, text='', **kwargs):
        self.init(kwargs)
        self.text = self.param(text, 'string', 'The text')

    def get_html(self, html):
        html.append(self.text)

    @classmethod
    def example(self):
        return Text('Hello world!')


class Script(BaseObject):
    def __init__(self, script=None, **kwargs):
        self.init(kwargs)
        self.script = self.param(script, 'JS', 'Javascript to execute')

    def get_html(self, html):
        html.append_js(self.script.js)


# class ContextItemPattern(Pattern):
#     def __init__(self, pattern, markdown_instance=None, extension=None, renderer=None):
#         self.extension = extension
#         super().__init__(pattern, markdown_instance)
#
#     def handleMatch(self, m):
#         arg_name = m.group(2).strip()
#         if arg_name in self.extension.context:
#             html = self.extension.renderer.render_string(self.extension.context[arg_name])
#             return html
#         else:
#             return arg_name
#
# class ContextPostprocessor(Postprocessor):
#     def __init__(self, extension=None):
#         self.extension = extension
#         super().__init__()
#
#     def run(self, text):
#         for match in re.finditer('{{(.*?)}}', text):
#             arg_name = match.group(1).strip()
#             if arg_name in self.extension.context:
#                 html = self.extension.renderer.render_string(self.extension.context[arg_name])
#             else:
#                 html = arg_name
#             text = re.sub(match.group(0), html, text)
#
#         return text
#
#
# class ContextExtension(Extension):
#     def __init__(self):
#         super().__init__()
#         self.renderer = None
#         self.context = []
#
#     def extendMarkdown(self, md, md_globals):
#         md.postprocessors.add('context', ContextPostprocessor(self), '_end')
#
#     def set_context(self, context, renderer):
#         self.context = context
#         self.renderer = renderer
#

class Markdown(BaseObject):
    """
    Render text as markdown. Shark objects can be rendered inside the markup with {{ }} tags
    and they are passed in through the keyword arguments.

    Several extensions are available:

    - markdown.extensions.codehilite
    - markdown.extensions.fenced_code
    - markdown.extensions.abbr
    - markdown.extensions.def_list
    - markdown.extensions.footnotes
    - markdown.extensions.tables
    - markdown.extensions.smart_strong
    - markdown.extensions.sane_lists
    - markdown.extensions.smarty
    - markdown.extensions.toc
    """
    def __init__(self, text=u'', **kwargs):
        self.init(kwargs)
        self.text = self.param(text, 'raw', 'Text to render as markdown')
        self.context = kwargs

    def get_html(self, html):
        extensions = [
            'markdown.extensions.codehilite',
            'markdown.extensions.fenced_code',
            'markdown.extensions.abbr',
            'markdown.extensions.def_list',
            'markdown.extensions.footnotes',
            'markdown.extensions.tables',
            'markdown.extensions.smart_strong',
            'markdown.extensions.sane_lists',
            'markdown.extensions.smarty',
            'markdown.extensions.toc'
        ]

        dirty = markdown(text=self.text, output_format='html5', extensions=extensions, extension_configs={
            'markdown.extensions.codehilite': {'css_class': 'highlight', 'noclasses': True}
        })
        clean = bleach.clean(dirty, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES)
        for match in re.finditer('{{(.*?)}}', clean):
            arg_name = match.group(1).strip()
            if arg_name in self.context:
                raw = html.render_string(self.context[arg_name])
            else:
                raw = arg_name
            clean = re.sub(match.group(0), raw, clean)

        html.append(clean)

    @classmethod
    def example(self):
        from shark.objects.layout import Panel

        return Markdown(
            "###Markdown is great###\n"
            "Many different styles are available through MarkDown:\n\n"
            "1. You can make text **bold**\n"
            "2. Or *italic*\n"
            "3. And even ***both***\n"
            "\n"
            "You can include shark objects:\n"
            "{{ panel }}"
            "\n"
            "Read more about markdown [here](http://markdown.org)",
            panel = Panel(
                header='Just a panel',
                items=LOREM_IPSUM
            )
        )

def onclick(text, javascript, row):
    for field_name, value in row.items():
        text = text.replace('{{' + field_name + '}}', (value if isinstance(value, str) else str(value)))
        javascript = javascript.replace('{{' + field_name + '}}', (value if isinstance(value, str) else str(value)))
    return Raw(u'<a style="cursor:pointer" onclick="' + javascript + u'">' + escape(text) + u'</a>')

def render_expression(expr, row):
    if inspect.isfunction(expr) or isinstance(expr, partial):
        return expr(row)
    else:
        return expr

def iff(column, test_value, true_expr, false_expr, row):
    match = False
    for field_name, value in row.items():
        if field_name == column and (value == test_value or (value is None and test_value is None)):
            match = True

    if match:
        return render_expression(true_expr, row)
    else:
        return render_expression(false_expr, row)


class Size(Enumeration):
    default = 0
    md = 1
    sm = 2
    xs = 3
    lg = 4


class ButtonStyle(Enumeration):
    default = 1
    primary = 2
    success = 3
    info = 4
    warning = 5
    danger = 6
    link = 7


class ButtonState(Enumeration):
    none = 0
    active = 1
    disabled = 2


class BackgroundColor(Enumeration):
    default = 0
    primary = 1
    success = 2
    info = 3
    warning = 4
    danger = 5

    @classmethod
    def name(cls, value):
        return ('bg-' + super(BackgroundColor, cls).name(value)) if value else ''


class ContextualColor(BackgroundColor):
    muted = 6

    @classmethod
    def name(cls, value):
        return ('text-'+ super(ContextualColor, cls).name(value).split('-')[-1]) if value else ''
