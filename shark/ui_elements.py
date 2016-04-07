import re

from django.utils.http import urlencode

from shark.settings import SharkSettings
from shark.text import Anchor
from .layout import Panel, multiple_div_row, Row, Paragraph
from .base import BaseObject, Collection, Default, Enumeration, iif, Raw


class BreadCrumbs(BaseObject):
    """
    Displays Breadcrumbs navigation. The non-keyword arguments are the crumbs. Add Anchors or simple text strings.
    """
    def __init__(self, *args, microdata=True, **kwargs):
        self.init(kwargs)
        self.crumbs = Collection(args)
        self.microdata = self.param(microdata, 'bool', 'Include microdata properties in the html. This might render the breadcrumbs in Google search results.')

    def get_html(self, html):
        html.append('<ol class="breadcrumb"{}>'.format(iif(self.microdata, ' itemscope itemtype="http://schema.org/BreadcrumbList"')))
        for i, crumb in enumerate(self.crumbs):
            if self.microdata and isinstance(crumb, Anchor):
                crumb.microdata = True
                html.append('    <li' + iif(i == len(self.crumbs) - 1, ' class="active"') + ' itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem">')
                html.render('        ', crumb)
                html.append('        <meta itemprop="position" content="{}" />'.format(i))
                html.append('    </li>')
            else:
                html.append('    <li' + iif(i == len(self.crumbs) - 1, ' class="active"') + '>')
                html.render('        ', crumb)
                html.append('    </li>')
        html.append('</ol>')

    @classmethod
    def example(self):
        return BreadCrumbs(Anchor('Home', '/'), Anchor('Docs', '/docs'), 'BreadCrumbs')


class ImageShape(Enumeration):
    default = 0
    rounded = 1
    circle = 2
    thumbnail = 3


class Image(BaseObject):
    """
    Displays an image.
    """
    def __init__(self, src='', alt='', responsive=True, shape=ImageShape.default, data_src='', **kwargs):
        self.init(kwargs)
        self._src = self.param(src, 'url', 'Src (Url) of the image')
        self.alt = self.param(alt, 'string', 'Alt for image')
        self.responsive = self.param(responsive, 'responsive', 'Src (Url) of the image', '')
        self.shape = self.param(shape, 'ImageShape', 'indicates the shape of the image')
        self.data_src = self.param(data_src, 'url', 'data-src of the image')
        if self.shape:
            self.add_class('img-' + ImageShape.name(self.shape))

    def get_html(self, html):
        if self.responsive:
            self.add_class('img-responsive')
        if self._src:
            src = 'src="{}"'.format(self._src)
        elif self.data_src:
            src = 'data-src="{}"'.format(self.data_src)

        html.append('<img {}'.format(src) + ' alt="{}"'.format(self.alt) + self.base_attributes + '/>')

    def src(self, src):
        return self.jq.attr('src', src)

    @classmethod
    def example(self):
        return Image('/static/web/img/bart_bg.jpg', 'Niagara Falls', shape=ImageShape.rounded)


class Thumbnail(BaseObject):
    """
    Displays an image in a frame with a caption. Useful for lists of thumbnails.
    """
    def __init__(self, img_url='', width=None, height=None, alt='', items=Default, **kwargs):
        self.init(kwargs)
        self.img_url = self.param(img_url, 'url', 'Link to the image')
        self.width = self.param(width, 'css_attr', 'Image width')
        self.height = self.param(height, 'css_attr', 'Image height')
        self.alt = self.param(alt, 'string', 'Alt text')
        self.items = self.param(items, 'Collection', 'Items under the image', Collection())

    def get_html(self, html):
        style = ''
        if self.width:
            style += u'width:' + str(self.width) + u';'
        if self.height:
            style += u'height:' + str(self.height) + u';'

        html.append(u'<div id="' + self.id + '" class="thumbnail">')
        html.append(u'    <img src="' + self.img_url + u'" alt="' + self.alt + '"' + (' style="' + style + '"' if style else '') + '>')
        html.append(u'    <div class="caption">')
        html.render(u'        ', self.items)
        html.append(u'    </div>')
        html.append(u'</div>')

    @classmethod
    def example(self):
        return multiple_div_row(
            Thumbnail('/static/web/img/bart.jpg', width='100%', items='Bart'),
            Thumbnail('/static/web/img/dylan.jpg', width='100%', items='Dylan'),
            Thumbnail('/static/web/img/mark.jpg', width='100%', items='Mark')
        )


class Progress(BaseObject):
    def __init__(self, percentage=0, **kwargs):
        self.init(kwargs)
        self.percentage = self.param(percentage, 'int', 'Percentage value')

    def get_html(self, html):
        html.append('<div class="progress">')
        html.append('    <div class="progress-bar" role="progressbar" aria-valuenow="' + str(self.percentage) + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + str(self.percentage) + '%;">')
        html.append('        ' + str(self.percentage) + '%')
        html.append('    </div>')
        html.append('</div>')

    @classmethod
    def example(self):
        return Progress(85)


class Address(BaseObject):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in Address', Collection())

    def get_html(self, html):
        html.append('<address>')
        html.render('    ', self.items)
        html.append('</address>')


class Carousel(BaseObject):
    """
    Creates a Bootstrap carousel.
    """
    def __init__(self, slides=Default, **kwargs):
        self.init(kwargs)
        self.slides = self.param(slides, 'list', 'List of slides.', [])
        self.id_needed = True

    def get_html(self, html):
        self.add_class('carousel slide')
        html.append('<div' + self.base_attributes + ' data-ride="carousel">')
        html.append('    <ol class="carousel-indicators">')
        for i, slide in enumerate(self.slides):
            html.append('        <li data-target="#carousel-example-generic" data-slide-to="{}"{}></li>'.format(i, ' class="active"' if i==0 else ''))
        html.append('    </ol>')

        html.append('    <div class="carousel-inner" role="listbox">')
        for i, slide in enumerate(self.slides):
            html.append('        <div class="item{}">'.format(' active' if i==0 else ''))
            html.render('            ', slide)
            # html.append('      <img src="..." alt="...">')
            # html.append('      <div class="carousel-caption">')
            # html.append('      </div>')
            html.append('        </div>')
        html.append('    </div>')

        html.append('    <a class="left carousel-control" href="#{}" role="button" data-slide="prev">'.format(self.id))
        html.append('        <span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>')
        html.append('        <span class="sr-only">Previous</span>')
        html.append('    </a>')
        html.append('    <a class="right carousel-control" href="#{}" role="button" data-slide="next">'.format(self.id))
        html.append('        <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>')
        html.append('        <span class="sr-only">Next</span>')
        html.append('    </a>')
        html.append('</div>')

        html.append_js('$("#{}").carousel()'.format(self.id))

    @classmethod
    def example(self):
        return Carousel([
            Image('/static/web/img/bart_bg.jpg'),
            Image('/static/web/img/dylan_bg.jpg'),
            Image('/static/web/img/mark_bg.jpg')
        ])


class Tab(BaseObject):
    def __init__(self, name='', items='', active=False, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'Collection', 'Name of the tab')
        self.items = self.param(items, 'Collection', 'Content of the tab')
        self.active = self.param(active, 'boolean', 'Make this the active tab. Defaults to the first tab')
        self.id_needed = True

    def get_html(self, html):
        html.append('<div' + self.base_attributes + ' role="tabpanel" class="tab-pane{}">'.format(' active' if self.active else ''))
        html.render('    ', self.items)
        html.append('</div>')


class Tabs(BaseObject):
    def __init__(self, tabs=None, **kwargs):
        self.init(kwargs)
        self.tabs = self.param(tabs, 'Collection', 'The list of Tab objects')
        self.id_needed = True

    def get_html(self, html):
        if not self.tabs:
            return None
        active_tab = None
        for tab in self.tabs:
            if tab.active:
                if active_tab is None:
                    active_tab = tab.active
                else:
                    tab.active = False
        if not active_tab:
            self.tabs[0].active = True

        html.append('<ul' + self.base_attributes + ' class="nav nav-tabs {}" role="tablist">'.format(
            html.add_css_class('margin-bottom: 15px;')
        ))
        for tab in self.tabs:
            html.append('    <li role="presentation"{}><a href="#{}" aria-controls="{}" role="tab" data-toggle="tab">'.format(
                ' class="active"' if tab.active else '',
                tab.id, tab.id
            ))
            html.render('    ', tab.name)
            html.append('</a></li>')
        html.append('</ul>')

        html.append('<div class="tab-content">')
        for tab in self.tabs:
            html.render('    ', tab)
        html.append('</div>')

        html.append_js('$("#' + self.id + ' a").click(function (e) {e.preventDefault(); $(this).tab("show")})')

    @classmethod
    def example(cls):
        return Tabs([
            Tab('Home', Paragraph('Home sweet home')),
            Tab('Away', Paragraph('Away from home'))
        ])


class CloseIcon(BaseObject):
    def __init__(self, js=None, **kwargs):
        self.init(kwargs)
        self.js = self.param(js, 'JS', 'Action when the the close icon is clicked')

    def get_html(self, html):
        html.append('<button type="button"' + self.base_attributes + self.js.onclick + ' class="close" aria-label="Close"><span aria-hidden="true">&times;</span></button>')

    @classmethod
    def example(cls):
        panel = Panel('Hello world')
        panel.append(CloseIcon(panel.jq.fadeOut().fadeIn()))
        return panel


class Caret(BaseObject):
    """
    Adds a caret. See the example.
    """
    def __init__(self, **kwargs):
        self.init(kwargs)

    def get_html(self, html):
        html.append('<span class="caret"></span>')


class Video(BaseObject):
    """
    Embed a video with the HTML video tag
    """
    def __init__(self, urls=Default, auto_play=False, aspect_ratio=0.5625, **kwargs):
        self.init(kwargs)
        self.urls = self.param(urls, 'list', 'List of urls of different versions of the video', [])
        self.auto_play = self.param(auto_play, 'boolean', 'Start the video automatically on load?')
        self.aspect_ratio = self.param(aspect_ratio, 'float', 'Aspect of video, used for iframed videos in fluid layouts')

    def get_html(self, html):
        self.id_needed = True
        if len(self.urls)==1 and self.urls[0].startswith('https://vimeo.com/'):
            video_id_match = re.match('https://vimeo.com/([0-9]*)', self.urls[0])
            if video_id_match:
                html.append('<div' + self.base_attributes + '><iframe src="https://player.vimeo.com/video/{}" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>'.format(video_id_match.group(1)))
        elif len(self.urls)==1 and self.urls[0].startswith('https://www.youtube.com/'):
            video_id_match = re.match('https://www\.youtube\.com/watch\?v=([-0-9a-zA-Z]*)', self.urls[0])
            if video_id_match:
                html.append('<div' + self.base_attributes + '><iframe src="https://www.youtube.com/embed/{}" frameborder="0" allowfullscreen></iframe></div>'.format(video_id_match.group(1)))
        else:
            html.append("<video" + self.base_attributes + " width='100%' controls{}>".format(iif(self.auto_play, ' autoplay')))
            for link in self.urls:
                html.append(u"    <source src='" + link + u"'>")
            html.append("</video>")

        if len(self.urls) == 1 and (self.urls[0].startswith('https://vimeo.com/') or self.urls[0].startswith('https://www.youtube.com/')):
            div = "$('#" + self.id + "')"
            iframe = "$('#" + self.id + " iframe')"
            html.append_js("$(window).resize(function(){" + iframe + ".width(" + div + ".width());" + iframe + ".height(" + iframe + ".width()*" + str(self.aspect_ratio) + ");}).resize();")

    def set_source(self, src):
        return "$('#{} source').attr('src', '{}');$('#{}')[0].load();".format(self.id, src, self.id)

    @classmethod
    def example(cls):
        return Video(urls='http://www.sample-videos.com/video/mp4/240/big_buck_bunny_240p_1mb.mp4')


class GoogleMaps(BaseObject):
    """
    Render a Google Maps map.

    Be sure to set the SHARK_GOOGLE_BROWSER_API_KEY setting in your settings.py.
    You can get this key in the [Google Developers API Console](https://console.developers.google.com/apis/library)
    """
    def __init__(self, location='', width='100%', height='250px', **kwargs):
        self.init(kwargs)
        self.location = self.param(location, 'string', 'Location name or "long, lat"')
        self.width = self.param(width, 'css', 'Width of the map in px or %')
        self.height = self.param(height, 'css', 'Height of the map in px or %')

    def get_html(self, html):
        html.append('<iframe' + self.base_attributes + ' width="{}" height="{}" frameborder="0" style="border:0" src="https://www.google.com/maps/embed/v1/place?key={}&{}" allowfullscreen></iframe>'.format(self.width, self.height, SharkSettings.SHARK_GOOGLE_BROWSER_API_KEY, urlencode({'q': self.location})))

    @classmethod
    def example(cls):
        return GoogleMaps('Fukuoka, Japan')


class SearchBox(BaseObject):
    def __init__(self, name='Search', button_name=Raw('<span class="glyphicon glyphicon-search"></span>'), url='/search', **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'Placeholder text')
        self.button_name = self.param(button_name, 'Collection', 'Text on the search button')
        self.url = self.param(url, 'url', 'Search URL')
        self.add_class('form-inline')

    def get_html(self, html):
        html.append('<form' + self.base_attributes + ' action="' + self.url + '" role="search">')
        html.append('    <div class="form-group">')
        html.append('        <div class="input-group">')
        html.append('            <input name="keywords" type="text" class="form-control" placeholder="' + self.name + '">')
        html.append('            <span class="input-group-btn">')
        html.append('                <button class="btn btn-default" type="submit">' + self.button_name.render() + '</button>')
        html.append('            </span>')
        html.append('        </div>')
        html.append('    </div>')
        html.append('</form>')


class Parallax(BaseObject):
    def __init__(self, background_url='', items=Default, speed=3, **kwargs):
        self.init(kwargs)
        self.background_url = self.param(background_url, 'url', 'URL to the background image')
        self.items = self.param(items, 'Collection', 'The items in the section', Collection())
        self.speed = self.param(speed, 'float', 'The speed of the parallax, higher numbers is slower. 1 is normal page speed, 2 is half speed, etc.')
        self.style += 'background: url({}) 50% 0/100% fixed; height: auto; margin: 0 auto; width: 100%; position: relative;'.format(self.background_url)
        self.id_needed = True

    def get_html(self, html):
        html.append('<section' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</section>')

        html.append_js("var scroll = $('#" + self.id + "'); $(window).scroll(function() {scroll.css({ backgroundPosition: '50% ' + (-($(window).scrollTop() / " + str(self.speed) + ")) + 'px' })});")


class Feature(BaseObject):
    def __init__(self, heading=None, explanation=None, demonstration=None, flipped=False, **kwargs):
        self.init(kwargs)
        self.heading = self.param(heading, 'Collection', 'Heading for the feature')
        self.explanation = self.param(explanation, 'Collection', 'Explanation of the feature')
        self.demonstration = self.param(demonstration, 'Collection', 'Something do demonstrate the feature, such as an image')
        self.flipped = self.param(flipped, 'boolean', 'Flip the explanation and demonstation. It looks good to alternate between features.')

    def get_html(self, html):
        def explanation():
            html.append('        <hr class="{}">'.format(html.add_css_class('float: left;width: 200px;border-top: 3px solid #e7e7e7;')))
            html.append('        <div class="clearfix"></div>')
            html.append('        <h2>')
            html.render('            ', self.heading)
            html.append('        </h2>')
            html.append('        <p class="lead">')
            html.render('            ', self.explanation)
            html.append('        </p>')

        def demonstration():
            html.render('        ', self.demonstration)


        html.append('<div class="row">')
        html.append('    <div class="col-lg-5 col-sm-6">')
        demonstration() if self.flipped else explanation()
        html.append('    </div>')
        html.append('    <div class="col-lg-5 col-lg-offset-2 col-sm-6">')
        explanation() if self.flipped else demonstration()
        html.append('    </div>')
        html.append('</div>')

