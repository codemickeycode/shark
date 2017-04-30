from shark.base import Enumeration, Object, StringParam
from shark.common import Default
from shark.objects.base import Raw
from shark.param_converters import ObjectsParam, UrlParam, BooleanParam


class NavBarPosition(Enumeration):
    none = 0
    static_top = 1
    fixed_top = 2
    fixed_bottom = 3


class NavBar(Object):
    def __init__(self, position=NavBarPosition.static_top, brand=None, items=None, search=None, right_items=Default, **kwargs):
        self.init(kwargs)
        self.position = self.param(position, NavBarPosition, 'Position of the NavBar')
        self.brand = self.param(brand, NavBrand, 'NavBrand for the NavBar')
        self.items = self.param(items, ObjectsParam, 'Items on the left side of the navbar')
        self.search = self.param(search, NavSearch, 'Search box')
        self.right_items = self.param(right_items, ObjectsParam, 'Items on the right side of the navbar')

    def get_html(self, html):
        if self.position == NavBarPosition.fixed_top:
            html.append_js("$(window).resize(function () {$('body').css('padding-top', parseInt($('#" + self.id + "').css('height')))});")
            html.append_js("$('body').css('padding-top', parseInt($('#" + self.id + "').css('height')));")
        elif self.position == NavBarPosition.fixed_bottom:
            html.append_js("$(window).resize(function () {$('body').css('padding-bottom', parseInt($('#" + self.id + "').css('height')))});")
            html.append_js("$('body').css('padding-bottom', parseInt($('#" + self.id + "').css('height')));")

        html.append('<nav' + self.base_attributes + ' class="navbar navbar-default navbar-{}">'.format(NavBarPosition.name(self.position).replace('_', '-')))
        html.append('    <div class="container-fluid">')
        html.append('        <div class="navbar-header">')
        html.append('            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#{}_items" aria-expanded="false">'.format(self.id))
        html.append('                <span class="sr-only">Toggle navigation</span>')
        html.append('                <span class="icon-bar"></span>')
        html.append('                <span class="icon-bar"></span>')
        html.append('                <span class="icon-bar"></span>')
        html.append('            </button>')
        html.render('            ', self.brand)
        html.append('        </div>')
        html.append('')
        html.append('        <div class="collapse navbar-collapse" id="{}_items">'.format(self.id))
        if self.items:
            html.append('            <ul class="nav navbar-nav">')
            html.render('                ', self.items)
            html.append('            </ul>')
        html.render('            ', self.search)
        if self.right_items:
            html.append('            <ul class="nav navbar-nav navbar-right">')
            html.render('                ', self.right_items)
            html.append('            </ul>')
        html.append('        </div>')
        html.append('    </div>')
        html.append('</nav>')

    @classmethod
    def example(cls):
        return NavBar(
            NavBarPosition.none,
            NavBrand('Example'),
            [
                NavDropDown(
                    'Sites',
                    [
                        NavLink('Google', 'http://google.com'),
                        NavLink('Yahoo', 'http://yahoo.com'),
                        NavDivider(),
                        NavLink('Bing',  'http://bing.com')
                    ]
                ),
                NavLink('Other', '#')
            ],
            NavSearch(),
            NavLink('Blog', '/blog')
        )


class SideNav(Object):
    def __init__(self, items=None, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Items on the left side of the navbar')

    def get_html(self, html):
        html.append('<nav' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</nav>')


class NavBrand(Object):
    def __init__(self, name=None, url='/', **kwargs):
        self.init(kwargs)
        self.name = self.param(name, ObjectsParam, 'Name and or logo of the application')
        self.url = self.param(url, UrlParam, 'URL to navigate to when the brand name is clicked')

    def get_html(self, renderer):
        renderer.append('<a' + self.base_attributes + ' class="navbar-brand"' + self.url.href(renderer) + '>')
        renderer.inline_render(self.name)
        renderer.append('</a>')


class NavLink(Object):
    def __init__(self, name=None, url=None, active=False, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, ObjectsParam, 'Name of the link')
        self.url = self.param(url, UrlParam, 'URL to navigate to when the item is clicked')
        self.active = self.param(active, BooleanParam, 'Display as activated')

    def get_html(self, renderer):
        if self.active:
            self.add_class('active')

        renderer.append('<li' + self.base_attributes + '><a' + self.url.href(renderer) + '>')
        renderer.render('    ', self.name)
        renderer.append('</a></li>')


class NavDivider(Object):
    def __init__(self, **kwargs):
        self.init(kwargs)

    def get_html(self, html):
        html.append('<li' + self.base_attributes + ' class="divider"></li>')


class NavDropDown(Object):
    def __init__(self, name=None, items=None, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, ObjectsParam, 'Heading of the dropdown')
        self.items = self.param(items, ObjectsParam, 'Items in the dropdown menu')

    def get_html(self, renderer):
        renderer.append('<li' + self.base_attributes + ' class="dropdown">')
        renderer.append('    <a href="#" class="dropdown-toggle" data-toggle="dropdown">')
        renderer.render('        ', self.name)
        renderer.append('        <b class="caret"></b>')
        renderer.append('    </a>')
        renderer.append('    <ul class="dropdown-menu">')
        renderer.render('        ', self.items)
        renderer.append('    </ul>')
        renderer.append('</li>')


class NavSearch(Object):
    def __init__(self, name='Search', button_name=Default, url='/search', **kwargs):
        self.init(kwargs)
        self.name = self.param(name, StringParam, 'Placeholder text')
        self.button_name = self.param(button_name, ObjectsParam, 'Text on the search button', Raw('<span class="glyphicon glyphicon-search"></span>'))
        self.url = self.param(url, StringParam, 'Search URL')
        self.add_class('navbar-form navbar-left')

    def get_html(self, renderer):
        renderer.append('<form' + self.base_attributes + ' action="' + self.url + '" role="search">')
        renderer.append('    <div class="form-group">')
        renderer.append('        <input name="keywords" type="text" class="form-control" placeholder="' + self.name + '">')
        renderer.append('    </div>')
        renderer.append('    <button type="submit" class="btn btn-default">')
        renderer.inline_render(self.button_name)
        renderer.append('</button>')
        renderer.append('</form>')


class Pills(Object):
    def __init__(self, items, stacked=False, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, "List of pills")
        self.stacked = self.param(stacked, BooleanParam, "Should the pills be vertically stacked?")

    def get_html(self, renderer):
        self.add_class('nav nav-pills')
        if self.stacked:
            self.add_class('nav-stacked')

        renderer.append('<ul' + self.base_attributes + '>')
        renderer.render('    ', self.items)
        renderer.append('</ul>')

    def activate(self, id_name):
        for pill in self.items:
            if isinstance(pill, Pill):
                pill.active = pill.id_name == id_name


class Pill(Object):
    def __init__(self, items=Default, action='', active=False, id_name='', **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, "Text/content on the pill")
        self.action = self.param(action, UrlParam, "Action when clicked")
        self.active = self.param(active, BooleanParam, "Is the pill active?")
        self.id_name = self.param(id_name, StringParam, "Internal name to activate the right pill")

    def get_html(self, renderer):
        if self.active:
            self.add_class('active')

        renderer.append('<li' + self.base_attributes + ' role="presentation"><a{}>'.format(self.action.href(renderer)))
        renderer.render('    ', self.items)
        renderer.append('</a></li>')
