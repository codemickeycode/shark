from .base import BaseObject, Default, Collection, Enumeration
from .resources import Resources


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


def use_theme(theme):
    Resources.replace_resource('https://maxcdn.bootstrapcdn.com/bootswatch/3.3.6/{}/bootstrap.min.css'.format(BootswatchTheme.name(theme)), 'css', 'bootstrap', 'main')


class Br(BaseObject):
    """
    Creates the <br/> html tag.
    """
    def __init__(self, **kwargs):
        self.init(kwargs)

    def get_html(self, html):
        html.append('<br' + self.base_attributes + '/>')

    @classmethod
    def example(cls):
        return ['First line', Br(), 'Second line']


class Row(BaseObject):
    """
    A Bootstrap Row.
    """
    def __init__(self, items=Default,  **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the row', Collection())

    def get_html(self, html):
        html.append('<div id="' + self.id + '" ' + ('class="row '+self.classes+'">' if self.classes else 'class="row">'))
        html.render('    ', self.items)
        html.append('</div>')

    def get_amp_html(self, html):
        html.append('<div id="' + self.id + '" ' + ('class="row '+self.classes+'">' if self.classes else 'class="row">'))
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
        return 'text-' + super(ParagraphStyle, cls).name(value)


class Paragraph(BaseObject):
    """
    Add a paragraph.
    """
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Content of the paragraph', Collection())

    def get_html(self, html):
        html.append('<p' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</p>')

    @classmethod
    def example(self):
        return Paragraph("This is a paragraph of text.")


class Lead(Paragraph):
    """
    Create a Bootstrap Lead.
    """
    def __init__(self, items=Default, **kwargs):
        super(Lead, self).__init__(items, **kwargs)
        self.add_class('lead')

    @classmethod
    def example(self):
        return Lead("This is a Bootstrap Lead.")


class Footer(BaseObject):
    """
    A footer.
    """
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the <footer>', Collection())

    def get_html(self, html):
        html.append(u'<footer ' + self.base_attributes + '>')
        html.render(u'    ', self.items)
        html.append(u'</footer>')

    @classmethod
    def example(self):
        return Footer("This is a footer.")


class Panel(BaseObject):
    """
    A Basic Panel.
    """
    def __init__(self, items=Default, header=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the panel', Collection())
        self.header = self.param(header, 'Collection', 'Header of the panel', Collection())
        self.classes = (self.classes + ' panel panel-default').strip()

    def get_html(self, html):
        html.append(u'<div' + self.base_attributes+ '>')
        if self.header:
            html.append('    <div class="panel-heading">')
            html.inline_render(self.header)
            html.append('    </div>')
        html.append(u'    <div class="panel-body">')
        html.render(u'        ', self.items)
        html.append(u'    </div>')
        html.append(u'</div>')

    def get_amp_html(self, html):
        html.append(u'<div' + self.base_attributes+ '>')
        if self.header:
            html.append('    <div class="panel-heading">')
            html.inline_render(self.header)
            html.append('    </div>')
        html.append(u'    <div class="panel-body">')
        html.render(u'        ', self.items)
        html.append(u'    </div>')
        html.append(u'</div>')

    @classmethod
    def example(self):
        return Panel("This is a Panel.")


class QuickFloat(Enumeration):
    default = 0
    left = 1
    right = 2

    @classmethod
    def name(cls, value):
        return ('pull-' + super(QuickFloat, cls).name(value)) if value else ''


class Div(BaseObject):
    """
    A flexible <div> element.
    """
    def __init__(self, items=Default, quick_float=QuickFloat.default, centered=False, clearfix=False, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the row', Collection())
        self.quick_float = self.param(quick_float, 'QuickFloat', 'Quick float to pull div left or right')
        self.centered = self.param(centered, 'boolean', 'Whether the div is center block')
        self.clearfix = self.param(clearfix, 'boolean', 'indicates whether to use clearfix')
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

    def get_amp_html(self, html):
        html.append('<div' + self.base_attributes + '>')
        html.render('', self.items)
        html.append('</div>')

    @classmethod
    def example(self):
        return Div('Content of the Div', quick_float=QuickFloat.right)


class Span(BaseObject):
    def __init__(self, text=Default, **kwargs):
        self.init(kwargs)
        self.text = self.param(text, 'Collection', 'The text', '')
        self.tag = u'span'

    def get_html(self, html):
        html.append('<' + self.tag + self.base_attributes + '>')
        html.inline_render(self.text)
        html.append('</' + self.tag + u'>')

    @classmethod
    def example(self):
        return Span('Text in the <span>...')


class Spacer(BaseObject):
    """
    Add some vertical spacing to your layout.
    """
    def __init__(self, pixels=20, **kwargs):
        self.init(kwargs)
        self.pixels = self.param(pixels, 'int', 'Vertical spacing in pixels')

    def get_html(self, html):
        html.append('<div style="height:{}px;"></div>'.format(self.pixels))

    @classmethod
    def example(self):
        return Collection(
            Paragraph('First paragraph...'),
            Spacer(40),
            Paragraph('Second paragraph after extra space.')
        )


class Main(BaseObject):
    """
    Adds a <main> section.
    """
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the <main>', Collection())

    def get_html(self, html):
        html.append(u'<main' + self.base_attributes + u'>')
        html.render('    ', self.items)
        html.append(u'</main>')


class Jumbotron(BaseObject):
    """
    Create a Bootstrap Jumbotron.
    """
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the container', Collection())

    def get_html(self, html):
        html.append(u'<div id="' + self.id + '" class="jumbotron web_object">')
        html.render(u'    ', self.items)
        html.append(u'</div>')

    @classmethod
    def example(self):
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
    row = Row([Div(Panel(content), classes=classes) for content in content_collections])
    return row


def multiple_div_row(*content_collections, **kwargs):
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
    row = Row([Div(content, classes=div_classes) for content in content_collections], **kwargs)
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
