from .base import BaseObject, Default, Collection


class UnorderedList(BaseObject):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'List items in <ul>', Collection())

    def get_html(self, html):
        html.append(u'<ul' + self.base_attributes + '>')
        html.render(u'    ', self.items)
        html.append(u'</ul>')


class HorizontalList(BaseObject):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'List items in list', Collection())
        self.classes += ' horizontal-list'

    def get_html(self, html):
        html.append(u'<ul' + self.base_attributes + '>')
        html.render(u'    ', self.items)
        html.append(u'</ul>')


class OrderedList(BaseObject):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'List items in <ol>', Collection())

    def get_html(self, html):
        html.append(u'<ol' + self.base_attributes + '>')
        html.render(u'    ', self.items)
        html.append(u'</ol>')


class DefinitionTerm(BaseObject):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Content of <dt>', Collection())

    def get_html(self, html):
        if self.items:
            html.append(u'<dt' + self.base_attributes + '>')
            html.render(u'    ', self.items)
            html.append(u'</dt>')


class DescriptionTerm(BaseObject):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Content of <dd>', Collection())

    def get_html(self, html):
        if self.items:
            html.append(u'<dd' + self.base_attributes + '>')
            html.render(u'    ', self.items)
            html.append(u'</dd>')


class DescriptionList(BaseObject):
    def __init__(self, items=Default, horizontal=False, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'list', 'A list of tuples', [])
        self.horizontal = self.param(horizontal, 'boolean', 'Whether to use horizontal', False)

        if self.horizontal:
            self.add_class('dl-horizontal')

    def get_html(self, html):
        html.append(u'<dl' + self.base_attributes + '>')
        for item in self.items:
            term, definition = item
            html.append('    <dt>')
            html.inline_render(term)
            html.append('</dt>')
            html.append('    <dd>')
            html.inline_render(definition)
            html.append('</dd>')
        html.append(u'</dl>')


class ListItem(BaseObject):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Content of <li>', Collection())

    def get_html(self, html):
        html.append(u'<li' + self.base_attributes + '>')
        html.render(u'    ', self.items)
        html.append(u'</li>')


