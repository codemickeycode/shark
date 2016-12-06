from shark.objects.font_awesome import Icon
from shark.base import Object, Default, Objects
from shark.param_converters import ObjectsParam, BooleanParam, ListParam


class UnorderedList(Object):
    def __init__(self, items=None, icon_list=False, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'List items in <ul>')
        self.icon_list = self.param(icon_list, BooleanParam, 'Use Font Awesome icons as bullets')

    def get_html(self, html):
        html.append('<ul' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</ul>')


class HorizontalList(Object):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'List items in list', Objects())
        self.add_class('horizontal-list')

    def get_html(self, html):
        html.append('<ul' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</ul>')


class OrderedList(Object):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'List items in <ol>', Objects())

    def get_html(self, html):
        html.append('<ol' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</ol>')


class DefinitionTerm(Object):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Content of <dt>', Objects())

    def get_html(self, html):
        if self.items:
            html.append('<dt' + self.base_attributes + '>')
            html.render('    ', self.items)
            html.append('</dt>')


class DescriptionTerm(Object):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Content of <dd>', Objects())

    def get_html(self, html):
        if self.items:
            html.append('<dd' + self.base_attributes + '>')
            html.render('    ', self.items)
            html.append('</dd>')


class DescriptionList(Object):
    def __init__(self, items=Default, horizontal=False, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ListParam, 'A list of tuples', [])
        self.horizontal = self.param(horizontal, BooleanParam, 'Whether to use horizontal', False)

        if self.horizontal:
            self.add_class('dl-horizontal')

    def get_html(self, html):
        html.append('<dl' + self.base_attributes + '>')
        for item in self.items:
            term, definition = item
            html.append('    <dt>')
            html.inline_render(term)
            html.append('</dt>')
            html.append('    <dd>')
            html.inline_render(definition)
            html.append('</dd>')
        html.append('</dl>')


class ListItem(Object):
    def __init__(self, items=None, icon='', **kwargs):
        if isinstance(icon, int):
            icon = Icon.name(icon)

        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Content of <li>')
        self.icon = self.param(icon, ObjectsParam, 'Font Awesome icon to use as bullet')

    def get_html(self, html):
        html.append('<li' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</li>')


