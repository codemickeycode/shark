from collections import Iterable

from shark.base import Object, Default, Objects, Enumeration
from shark.objects.enumerations import QuickFloat
from shark.param_converters import ObjectsParam, BooleanParam, IntegerParam
from shark.resources import Resource


class BootswatchTheme(Enumeration):
    cerulean = 1
    cosmo = 2
    custom = 3
    cyborg = 4
    darkly = 5
    flatly = 6
    journal = 7
    lumen = 8
    paper = 9
    readable = 10
    sandstone = 11
    simplex = 12
    slate = 13
    spacelab = 14
    superhero = 15
    united = 16
    yeti = 17


def get_theme_resource(theme):
    if isinstance(theme, str):
        return Resource('https://maxcdn.bootstrapcdn.com/bootswatch/3.3.6/{}/bootstrap.min.css'.format(theme), 'css', 'bootstrap', 'main')
    else:
        return Resource('https://maxcdn.bootstrapcdn.com/bootswatch/3.3.6/{}/bootstrap.min.css'.format(BootswatchTheme.name(theme)), 'css', 'bootstrap', 'main')


class ThemeMeta(type):
    @property
    def cerulean(cls): return cls('cerulean')

    @property
    def cosmo(cls): return cls('cosmo')

    @property
    def custom(cls): return cls('custom')

    @property
    def cyborg(cls): return cls('cyborg')

    @property
    def darkly(cls): return cls('darkly')

    @property
    def flatly(cls): return cls('flatly')

    @property
    def journal(cls): return cls('journal')

    @property
    def lumen(cls): return cls('lumen')

    @property
    def paper(cls): return cls('paper')

    @property
    def readable(cls): return cls('readable')

    @property
    def sandstone(cls): return cls('sandstone')

    @property
    def readable(cls): return cls('readable')

    @property
    def simplex(cls): return cls('simplex')

    @property
    def slate(cls): return cls('slate')

    @property
    def spacelab(cls): return cls('spacelab')

    @property
    def superhero(cls): return cls('superhero')

    @property
    def united(cls): return cls('united')

    @property
    def yeti(cls): return cls('yeti')


class Theme(Object, metaclass=ThemeMeta):
    """
    Select a bootstrap Theme
    """
    def __init__(self, theme='cerulean', **kwargs):
        self.init(kwargs)
        self.theme = self.param(theme, BootswatchTheme, 'The theme')

    def get_html(self, html):
        theme_name = BootswatchTheme.name(self.theme)
        html.replace_resource('https://maxcdn.bootstrapcdn.com/bootswatch/3.3.6/{}/bootstrap.min.css'.format(theme_name), 'css', 'bootstrap', 'main')


class Br(Object):
    """
    Creates the &lt;br/&gt; html tag.
    """
    def __init__(self, **kwargs):
        self.init(kwargs)

    def get_html(self, html):
        html.append('<br' + self.base_attributes + '/>')

    @classmethod
    def example(cls):
        return ['First line', Br(), 'Second line']


class Row(Object):
    """
    A Bootstrap Row.
    """
    def __init__(self, items=None,  **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Items in the row')
        self.add_class('row')

    def get_html(self, html):
        html.append('<div' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</div>')


class ParagraphStyle(Enumeration):
    left = 0
    center = 1
    right = 2
    justify = 3
    nowrap = 4
    lowercase = 5
    uppercase = 6
    capitalize = 7

    @classmethod
    def name(cls, value):
        return 'text-' + cls.name(value)


class Paragraph(Object):
    """
    Add a paragraph.
    """
    def __init__(self, items=None, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Content of the paragraph')

    def get_html(self, html):
        html.append('<p' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</p>')

    @classmethod
    def example(cls):
        return Paragraph("This is a paragraph of text.")


class Lead(Paragraph):
    """
    Create a Bootstrap Lead.
    """
    def __init__(self, items=None, **kwargs):
        super().__init__(items, **kwargs)
        self.add_class('lead')

    @classmethod
    def example(cls):
        return Lead("This is a Bootstrap Lead.")


class Footer(Object):
    """
    A footer.
    """
    def __init__(self, items=None, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Items in the <footer>', Objects())

    def get_html(self, html):
        html.append('<footer ' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</footer>')

    @classmethod
    def example(cls):
        return Footer("This is a footer.")


class Panel(Object):
    """
    A Basic Panel.
    """
    def __init__(self, items=None, header=None, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Items in the panel', Objects())
        self.header = self.param(header, ObjectsParam, 'Header of the panel', Objects())
        self.add_class('panel panel-default')

    def get_html(self, html):
        html.append('<div' + self.base_attributes + '>')
        if self.header:
            html.append('    <div class="panel-heading">')
            html.inline_render(self.header)
            html.append('    </div>')
        html.append('    <div class="panel-body">')
        html.render('        ', self.items)
        html.append('    </div>')
        html.append('</div>')

    @classmethod
    def example(cls):
        return Panel("This is a Panel.")


class Div(Object):
    """
    A flexible &lt;div&gt; element.
    """
    def __init__(self, items=None, quick_float=None, centered=False, clearfix=False, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Items in the row', Objects())
        self.quick_float = self.param(quick_float, QuickFloat, 'Quick float to pull div left or right')
        self.centered = self.param(centered, BooleanParam, 'Whether the div is center block')
        self.clearfix = self.param(clearfix, BooleanParam, 'indicates whether to use clearfix')
        if self.quick_float:
            self.add_class(QuickFloat.name(self.quick_float))
        if self.centered:
            self.add_class('center-box')
        if self.clearfix:
            self.add_class('clearfix')

    def get_html(self, html):
        html.append('<div' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</div>')

    @classmethod
    def example(cls):
        return Div('Content of the Div', quick_float=QuickFloat.right)


class Span(Object):
    def __init__(self, text=Default, **kwargs):
        self.init(kwargs)
        self.text = self.param(text, ObjectsParam, 'The text', '')
        self.tag = 'span'

    def get_html(self, html):
        html.append('<' + self.tag + self.base_attributes + '>')
        html.inline_render(self.text)
        html.append('</' + self.tag + '>')

    @classmethod
    def example(cls):
        return Span('Text in the <span>...')


class Spacer(Object):
    """
    Add some vertical spacing to your layout.
    """
    def __init__(self, pixels=20, **kwargs):
        self.init(kwargs)
        self.pixels = self.param(pixels, IntegerParam, 'Vertical spacing in pixels')

    def get_html(self, html):
        html.append('<div' + self.base_attributes + ' style="height:{}px;"></div>'.format(self.pixels))

    @classmethod
    def example(cls):
        return Objects(
            Paragraph('First paragraph...'),
            Spacer(40),
            Paragraph('Second paragraph after extra space.')
        )


class Main(Object):
    """
    Adds a &lt;main&gt; section.
    """
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Items in the <main>', Objects())

    def get_html(self, html):
        html.append('<main' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</main>')


class Jumbotron(Object):
    """
    Create a Bootstrap Jumbotron.
    """
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Items in the container', Objects())
        self.add_class('jumbotron')

    def get_html(self, html):
        html.append('<div' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</div>')

    @classmethod
    def example(cls):
        return Jumbotron("Check this out!")


def multiple_panel_row(*content_collections):
    if len(content_collections) == 1:
        classes = "col-md-12 col-sm-12"
    elif len(content_collections) == 2:
        classes = "col-md-6 col-sm-12"
    elif len(content_collections) == 3:
        classes = "col-md-4 col-sm-6"
    elif len(content_collections) == 4:
        classes = "col-md-3 col-sm-6"
    else:
        classes = "col-md-4 col-sm-6"
    row = Row([Div(Panel(content), _class=classes) for content in content_collections])
    return row


def multiple_div_row(*content_collections, support_iterable=True, **kwargs):
    if support_iterable and len(content_collections) == 1 and not isinstance(content_collections, str) and isinstance(content_collections, Iterable):
        content_collections = content_collections[0]

    if len(content_collections) == 1:
        div_classes = "col-md-12 col-sm-12"
    elif len(content_collections) == 2:
        div_classes = "col-md-6 col-sm-12"
    elif len(content_collections) == 3:
        div_classes = "col-md-4 col-sm-6"
    elif len(content_collections) == 4:
        div_classes = "col-md-3 col-sm-6"
    else:
        div_classes = "col-md-4 col-sm-6"
    row = Row([Div(content, _class=div_classes) for content in content_collections], **kwargs)
    return row


def multiple_object_row(*content_collections, **kwargs):
    if len(content_collections) == 1:
        classes = "col-md-12 col-sm-12"
    elif len(content_collections) == 2:
        classes = "col-md-6 col-sm-12"
    elif len(content_collections) == 3:
        classes = "col-md-4 col-sm-6"
    elif len(content_collections) == 4:
        classes = "col-md-3 col-sm-6"
    else:
        classes = "col-md-4 col-sm-6"
    row = Row(**kwargs)
    for content in content_collections:
        content.add_class(classes)
        row.append(content)
    return row


def two_column(main_column, side_column, main_width=8):
    return Row([
        Div(main_column, classes='col-md-{}'.format(main_width)),
        Div(side_column, classes='col-md-{}'.format(12-main_width))
    ])
