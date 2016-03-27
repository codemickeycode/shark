from .base import BaseObject, Default, Raw, Collection, Enumeration


class NavBarPosition(Enumeration):
    none = 0
    static_top = 1
    fixed_top = 2
    fixed_bottom = 3


class NavBar(BaseObject):
    def __init__(self, position=NavBarPosition.static_top, brand=Default, items=Default, search=None, right_items=Default, **kwargs):
        self.init(kwargs)
        self.position = self.param(position, 'NavBarPosition', 'Position of the NavBar')
        self.brand = self.param(brand, 'NavBrand', 'NavBrand for the NavBar')
        self.items = self.param(items, 'Collection', 'Items on the left side of the navbar', Collection())
        self.search = self.param(search, 'NavSearch', 'Search box')
        self.right_items = self.param(right_items, 'Collection', 'Items on the right side of the navbar', Collection())

    def get_html(self, html):
        html.append(u'<nav' + self.base_attributes + u' class="navbar navbar-default navbar-{}">'.format(NavBarPosition.name(self.position).replace('_', '-')))
        html.append(u'    <div class="container-fluid">')
        html.append(u'        <div class="navbar-header">')
        html.append(u'            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#{}_items" aria-expanded="false">'.format(self.id))
        html.append(u'                <span class="sr-only">Toggle navigation</span>')
        html.append(u'                <span class="icon-bar"></span>')
        html.append(u'                <span class="icon-bar"></span>')
        html.append(u'                <span class="icon-bar"></span>')
        html.append(u'            </button>')
        html.render(u'            ', self.brand)
        html.append(u'        </div>')
        html.append(u'')
        html.append(u'        <div class="collapse navbar-collapse" id="{}_items">'.format(self.id))
        if self.items:
            html.append(u'            <ul class="nav navbar-nav">')
            html.render(u'                ', self.items)
            html.append(u'            </ul>')
        html.render(u'            ', self.search)
        if self.right_items:
            html.append(u'            <ul class="nav navbar-nav navbar-right">')
            html.render(u'                ', self.right_items)
            html.append(u'            </ul>')
        html.append(u'        </div>')
        html.append(u'    </div>')
        html.append(u'</nav>')

    def get_amp_html(self, html):
        html.append(u'<nav' + self.base_attributes + u' class="navbar navbar-default navbar-{}">'.format(NavBarPosition.name(self.position).replace('_', '-')))
        html.append(u'    <div class="container-fluid">')
        html.append(u'        <div class="navbar-header">')
        html.append(u'            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#{}_items" aria-expanded="false">'.format(self.id))
        html.append(u'                <span class="sr-only">Toggle navigation</span>')
        html.append(u'                <span class="icon-bar"></span>')
        html.append(u'                <span class="icon-bar"></span>')
        html.append(u'                <span class="icon-bar"></span>')
        html.append(u'            </button>')
        html.render(u'            ', self.brand)
        html.append(u'        </div>')
        html.append(u'')
        html.append(u'        <div class="collapse navbar-collapse" id="{}_items">'.format(self.id))
        if self.items:
            html.append(u'            <ul class="nav navbar-nav">')
            html.render(u'                ', self.items)
            html.append(u'            </ul>')
        html.render(u'            ', self.search)
        if self.right_items:
            html.append(u'            <ul class="nav navbar-nav navbar-right">')
            html.render(u'                ', self.right_items)
            html.append(u'            </ul>')
        html.append(u'        </div>')
        html.append(u'    </div>')
        html.append(u'</nav>')

    def render_css(self, indent=''):
        if self.position == NavBarPosition.fixed_top:
            return 'body { margin-top: 80px; }'
        elif self.position == NavBarPosition.fixed_bottom:
            return 'body { margin-bottom: 80px; }'

    @classmethod
    def example(self):
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


class SideNav(BaseObject):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items on the left side of the navbar', Collection())

    def get_html(self, html):
        html.append(u'<nav' + self.base_attributes + '>')
        html.render(u'    ', self.items)
        html.append(u'</nav>')


class NavBrand(BaseObject):
    def __init__(self, name=Default, url='/', **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'Collection', 'Name and or logo of the application', Collection())
        self.url = self.param(url, 'url', 'URL to navigate to when the brand name is clicked')

    def get_html(self, html):
        html.append('<a' + self.base_attributes + ' class="navbar-brand" href="' + self.url + '">')
        html.inline_render(self.name)
        html.append('</a>')

    def get_amp_html(self, html):
        html.append('<a' + self.base_attributes + ' class="navbar-brand" href="' + self.url + '">')
        html.inline_render(self.name)
        html.append('</a>')


class NavLink(BaseObject):
    def __init__(self, name=Default, url=None, active=False, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'Collection', 'Name of the link', Collection())
        self.url = self.param(url, 'url', 'URL to navigate to when the item is clicked')
        self.active = self.param(active, 'boolean', 'Display as activated')

    def get_html(self, html):
        if self.active:
            self.add_class('active')

        if self.url:
            html.append('<li' + self.base_attributes + '><a href="' + self.url + '">')
            html.render('    ', self.name)
            html.append('</a></li>')
        else:
            html.append('<li' + self.base_attributes + '><a href="#">')
            html.render('    ', self.name)
            html.append('</a></li>')


class NavDivider(BaseObject):
    def __init__(self, **kwargs):
        self.init(kwargs)

    def get_html(self, html):
        html.append('<li' + self.base_attributes + '" class="divider"></li>')


class NavDropDown(BaseObject):
    def __init__(self, name='', items=Default, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'Name of the application')
        self.items = self.param(items, 'Collection', 'Items in the dropdown menu', Collection())

    def get_html(self, html):
        html.append('<li' + self.base_attributes + ' class="dropdown">')
        html.append('    <a href="#" class="dropdown-toggle" data-toggle="dropdown">' + self.name + ' <b class="caret"></b></a>')
        html.append('    <ul class="dropdown-menu">')
        html.render('        ', self.items)
        html.append('    </ul>')
        html.append('</li>')


class NavSearch(BaseObject):
    def __init__(self, name='Search', button_name=Raw('<span class="glyphicon glyphicon-search"></span>'), url='/search', **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'Placeholder text')
        self.button_name = self.param(button_name, 'Collection', 'Text on the search button')
        self.url = self.param(url, 'url', 'Search URL')

    def get_html(self, html):
        html.append('<form id="' + self.id + '" action="' + self.url + '" class="navbar-form navbar-left web_object" role="search">')
        html.append('    <div class="form-group">')
        html.append('        <input name="keywords" type="text" class="form-control" placeholder="' + self.name + '">')
        html.append('    </div>')
        html.append('    <button type="submit" class="btn btn-default">')
        html.inline_render(self.button_name)
        html.append(    '</button>')
        html.append('</form>')


