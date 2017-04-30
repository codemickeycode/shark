import re
from shark.base import Objects, Default, Enumeration, Object, StringParam
from shark.dependancies import escape_url
from shark.objects.base import Raw
from shark.objects.layout import Panel, multiple_div_row, Paragraph
from shark.objects.text import Anchor
from shark.param_converters import BooleanParam, UrlParam, IntegerParam, ObjectsParam, JavascriptParam, FloatParam, \
    CssAttributeParam, ListParam
from shark.settings import SharkSettings


class BreadCrumbs(Object):
    """
    Displays Breadcrumbs navigation. The non-keyword arguments are the crumbs. Add Anchors or simple text strings.
    """
    def __init__(self, *args, microdata=True, **kwargs):
        self.init(kwargs)
        self.crumbs = Objects(args)
        self.microdata = self.param(microdata, BooleanParam, 'Include microdata properties in the renderer. This might render the breadcrumbs in Google search results.')

    def get_html(self, renderer):
        renderer.append('<ol class="breadcrumb"{}>'.format(' itemscope itemtype="http://schema.org/BreadcrumbList"' if self.microdata else ''))
        for i, crumb in enumerate(self.crumbs):
            if self.microdata and isinstance(crumb, Anchor):
                crumb.microdata = True
                renderer.append('    <li' + (' class="active"' if i == len(self.crumbs) - 1 else '') + ' itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem">')
                renderer.render('        ', crumb)
                renderer.append('        <meta itemprop="position" content="{}" />'.format(i))
                renderer.append('    </li>')
            else:
                renderer.append('    <li' + (' class="active"' if i == len(self.crumbs) - 1 else '') + '>')
                renderer.render('        ', crumb)
                renderer.append('    </li>')
        renderer.append('</ol>')

    @classmethod
    def example(cls):
        return BreadCrumbs(Anchor('Home', '/'), Anchor('Docs', '/docs'), 'BreadCrumbs')


class ImageShape(Enumeration):
    default = 0
    rounded = 1
    circle = 2
    thumbnail = 3


class Image(Object):
    """
    Displays an image.
    """
    def __init__(self, src='', alt='', responsive=True, shape=ImageShape.default, data_src='', **kwargs):
        self.init(kwargs)
        self._src = self.param(src, UrlParam, 'Src (Url) of the image')
        self.alt = self.param(alt, StringParam, 'Alt for image')
        self.responsive = self.param(responsive, BooleanParam, 'Responsive image', '')
        self.shape = self.param(shape, ImageShape, 'indicates the shape of the image')
        self.data_src = self.param(data_src, UrlParam, 'data-src of the image')
        if self.shape:
            self.add_class('img-' + ImageShape.name(self.shape))

    def get_html(self, renderer):
        if self.responsive:
            self.add_class('img-responsive')
        if self._src:
            src = 'src="{}"'.format(self._src)
        elif self.data_src:
            src = 'data-src="{}"'.format(self.data_src)
        else:
            src = ''

        renderer.append('<img {}'.format(src) + ' alt="{}"'.format(self.alt) + self.base_attributes + '/>')

    def src(self, src):
        return self.jq.attr('src', src)

    @classmethod
    def example(cls):
        return Image('/static/web/img/bart_bg.jpg', 'Niagara Falls', shape=ImageShape.rounded)


class Thumbnail(Object):
    """
    Displays an image in a frame with a caption. Useful for lists of thumbnails.
    """
    def __init__(self, img_url='', width=None, height=None, alt='', items=Default, **kwargs):
        self.init(kwargs)
        self.img_url = self.param(img_url, UrlParam, 'Link to the image')
        self.width = self.param(width, CssAttributeParam, 'Image width')
        self.height = self.param(height, CssAttributeParam, 'Image height')
        self.alt = self.param(alt, StringParam, 'Alt text')
        self.items = self.param(items, ObjectsParam, 'Items under the image', Objects())
        self.add_class('thumbnail')

    def get_html(self, renderer):
        style = ''
        if self.width:
            style += 'width:' + str(self.width) + ';'
        if self.height:
            style += 'height:' + str(self.height) + ';'

        renderer.append('<div' + self.base_attributes + '>')
        renderer.append('    <img src="' + self.img_url.url(renderer) + '" alt="' + self.alt + '"' + (' style="' + style + '"' if style else '') + '>')
        renderer.append('    <div class="caption">')
        renderer.render('        ', self.items)
        renderer.append('    </div>')
        renderer.append('</div>')

    @classmethod
    def example(cls):
        return multiple_div_row(
            Thumbnail('/static/web/img/bart.jpg', width='100%', items='Bart'),
            Thumbnail('/static/web/img/dylan.jpg', width='100%', items='Dylan'),
            Thumbnail('/static/web/img/mark.jpg', width='100%', items='Mark')
        )


class Progress(Object):
    def __init__(self, percentage=0, **kwargs):
        self.init(kwargs)
        self.percentage = self.param(percentage, IntegerParam, 'Percentage value')

    def get_html(self, renderer):
        renderer.append('<div class="progress">')
        renderer.append('    <div class="progress-bar" role="progressbar" aria-valuenow="' + str(self.percentage) + '" aria-valuemin="0" aria-valuemax="100" style="width: ' + str(self.percentage) + '%;">')
        renderer.append('        ' + str(self.percentage) + '%')
        renderer.append('    </div>')
        renderer.append('</div>')

    @classmethod
    def example(cls):
        return Progress(85)


class Address(Object):
    def __init__(self, items=Default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, ObjectsParam, 'Items in Address', Objects())

    def get_html(self, renderer):
        renderer.append('<address>')
        renderer.render('    ', self.items)
        renderer.append('</address>')


class Carousel(Object):
    """
    Creates a Bootstrap carousel.
    """
    def __init__(self, slides=Default, **kwargs):
        self.init(kwargs)
        self.slides = self.param(slides, ListParam, 'List of slides.', [])
        self.id_needed()

    def get_html(self, renderer):
        self.add_class('carousel slide')
        renderer.append('<div' + self.base_attributes + ' data-ride="carousel">')
        renderer.append('    <ol class="carousel-indicators">')
        for i, slide in enumerate(self.slides):
            renderer.append('        <li data-target="#carousel-example-generic" data-slide-to="{}"{}></li>'.format(i, ' class="active"' if i==0 else ''))
        renderer.append('    </ol>')

        renderer.append('    <div class="carousel-inner" role="listbox">')
        for i, slide in enumerate(self.slides):
            renderer.append('        <div class="item{}">'.format(' active' if i==0 else ''))
            renderer.render('            ', slide)
            # renderer.append('      <img src="..." alt="...">')
            # renderer.append('      <div class="carousel-caption">')
            # renderer.append('      </div>')
            renderer.append('        </div>')
        renderer.append('    </div>')

        renderer.append('    <a class="left carousel-control" href="#{}" role="button" data-slide="prev">'.format(self.id))
        renderer.append('        <span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>')
        renderer.append('        <span class="sr-only">Previous</span>')
        renderer.append('    </a>')
        renderer.append('    <a class="right carousel-control" href="#{}" role="button" data-slide="next">'.format(self.id))
        renderer.append('        <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>')
        renderer.append('        <span class="sr-only">Next</span>')
        renderer.append('    </a>')
        renderer.append('</div>')

        renderer.append_js('$("#{}").carousel()'.format(self.id))

    @classmethod
    def example(cls):
        return Carousel([
            Image('/static/web/img/bart_bg.jpg'),
            Image('/static/web/img/dylan_bg.jpg'),
            Image('/static/web/img/mark_bg.jpg')
        ])


class Tab(Object):
    def __init__(self, name=None, items=None, active=False, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, ObjectsParam, 'Name of the tab')
        self.items = self.param(items, ObjectsParam, 'Content of the tab')
        self.active = self.param(active, BooleanParam, 'Make this the active tab. Defaults to the first tab')
        self.id_needed()

    def get_html(self, renderer):
        renderer.append('<div' + self.base_attributes + ' role="tabpanel" class="tab-pane{}">'.format(' active' if self.active else ''))
        renderer.render('    ', self.items)
        renderer.append('</div>')


class Tabs(Object):
    def __init__(self, tabs=None, **kwargs):
        self.init(kwargs)
        self.tabs = self.param(tabs, ObjectsParam, 'The list of Tab objects')
        self.id_needed()

    def get_html(self, renderer):
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

        renderer.append('<ul' + self.base_attributes + ' class="nav nav-tabs {}" role="tablist">'.format(
            renderer.add_css_class('margin-bottom: 15px;')
        ))
        for tab in self.tabs:
            renderer.append('    <li role="presentation"{}><a href="#{}" aria-controls="{}" role="tab" data-toggle="tab">'.format(
                ' class="active"' if tab.active else '',
                tab.id, tab.id
            ))
            renderer.render('    ', tab.name)
            renderer.append('</a></li>')
        renderer.append('</ul>')

        renderer.append('<div class="tab-content">')
        for tab in self.tabs:
            renderer.render('    ', tab)
        renderer.append('</div>')

        renderer.append_js('$("#' + self.id + ' a").click(function (e) {e.preventDefault(); $(this).tab("show")})')

    @classmethod
    def example(cls):
        return Tabs([
            Tab('Home', Paragraph('Home sweet home')),
            Tab('Away', Paragraph('Away from home'))
        ])


class CloseIcon(Object):
    def __init__(self, js=None, **kwargs):
        self.init(kwargs)
        self.js = self.param(js, JavascriptParam, 'Action when the the close icon is clicked')

    def get_html(self, renderer):
        renderer.append('<button type="button"' + self.base_attributes + self.js.onclick(renderer) + ' class="close" aria-label="Close"><span aria-hidden="true">&times;</span></button>')

    @classmethod
    def example(cls):
        panel = Panel('Hello world')
        panel += CloseIcon(panel.jq.fadeOut().fadeIn())
        return panel


class Caret(Object):
    """
    Adds a caret. See the example.
    """
    def __init__(self, **kwargs):
        self.init(kwargs)

    def get_html(self, renderer):
        renderer.append('<span class="caret"></span>')


class Video(Object):
    """
    Embed a video with the HTML video tag
    Urls should point to the mp4 streams.
    You can also use Vimeo and YouTube links, but only if you only use a single url.
    """
    def __init__(self, urls=Default, auto_play=False, aspect_ratio=0.5625, **kwargs):
        self.init(kwargs)
        self.urls = self.param(urls, ListParam, 'List of urls of different versions of the video', [])
        self.auto_play = self.param(auto_play, BooleanParam, 'Start the video automatically on load?')
        self.aspect_ratio = self.param(aspect_ratio, FloatParam, 'Aspect of video, used for iframed videos in fluid layouts')

    def get_html(self, renderer):
        self.id_needed()
        if len(self.urls)==1 and self.urls[0].startswith('https://vimeo.com/'):
            video_id_match = re.match('https://vimeo.com/([0-9]*)', self.urls[0])
            if video_id_match:
                renderer.append('<div' + self.base_attributes + '><iframe src="https://player.vimeo.com/video/{}" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div>'.format(video_id_match.group(1)))
        elif len(self.urls)==1 and self.urls[0].startswith('https://www.youtube.com/'):
            video_id_match = re.match('https://www\.youtube\.com/watch\?v=([-0-9a-zA-Z]*)', self.urls[0])
            if video_id_match:
                renderer.append('<div' + self.base_attributes + '><iframe src="https://www.youtube.com/embed/{}" frameborder="0" allowfullscreen></iframe></div>'.format(video_id_match.group(1)))
        else:
            renderer.append("<video" + self.base_attributes + " width='100%' controls{}>".format(' autoplay' if self.auto_play else ''))
            for link in self.urls:
                renderer.append(u"    <source src='" + link + u"'>")
            renderer.append("</video>")

        if len(self.urls) == 1 and (self.urls[0].startswith('https://vimeo.com/') or self.urls[0].startswith('https://www.youtube.com/')):
            div = "$('#" + self.id + "')"
            iframe = "$('#" + self.id + " iframe')"
            renderer.append_js("$(window).resize(function(){" + iframe + ".width(" + div + ".width());" + iframe + ".height(" + iframe + ".width()*" + str(self.aspect_ratio) + ");}).resize();")

    def set_source(self, src):
        return "$('#{} source').attr('src', '{}');$('#{}')[0].load();".format(self.id, src, self.id)

    @classmethod
    def example(cls):
        return Video(urls='https://www.youtube.com/watch?v=cK3NMZAUKGw')


class IFrame(Object):
    """
    Render an IFrame.
    """
    def __init__(self, url='', width='100%', height='250px', **kwargs):
        self.init(kwargs)
        self.url = self.param(url, UrlParam, 'Iframe source URL')
        self.width = self.param(width, CssAttributeParam, 'Width of the frame in px or %')
        self.height = self.param(height, CssAttributeParam, 'Height of the frame in px or %')

    def get_html(self, renderer):
        renderer.append('<iframe' + self.base_attributes + ' width="{}" height="{}" frameborder="0" style="border:0" src="{}"></iframe>'.format(self.width, self.height, self.url))

    @classmethod
    def example(cls):
        return IFrame('http://example.com/')


class GoogleMaps(Object):
    """
    Render a Google Maps map.

    Be sure to set the SHARK_GOOGLE_BROWSER_API_KEY setting in your settings.py.
    You can get this key in the [Google Developers API Console](https://console.developers.google.com/apis/library)
    """
    def __init__(self, location='', width='100%', height='250px', **kwargs):
        self.init(kwargs)
        self.location = self.param(location, StringParam, 'Location name or "long, lat"')
        self.width = self.param(width, CssAttributeParam, 'Width of the map in px or %')
        self.height = self.param(height, CssAttributeParam, 'Height of the map in px or %')

    def get_html(self, renderer):
        renderer.append('<iframe' + self.base_attributes + ' width="{}" height="{}" frameborder="0" style="border:0" src="https://www.google.com/maps/embed/v1/place?key={}&q={}" allowfullscreen></iframe>'.format(self.width, self.height, SharkSettings.SHARK_GOOGLE_BROWSER_API_KEY, self.location))

    @classmethod
    def example(cls):
        return GoogleMaps('Fukuoka, Japan')


class SearchBox(Object):
    def __init__(self, name='Search', button_name=Raw('<span class="glyphicon glyphicon-search"></span>'), url='/search', **kwargs):
        self.init(kwargs)
        self.name = self.param(name, StringParam, 'Placeholder text')
        self.button_name = self.param(button_name, ObjectsParam, 'Text on the search button')
        self.url = self.param(url, UrlParam, 'Search URL')
        self.add_class('form-inline')

    def get_html(self, renderer):
        renderer.append('<form' + self.base_attributes + ' action="' + self.url + '" role="search">')
        renderer.append('    <div class="form-group">')
        renderer.append('        <div class="input-group">')
        renderer.append('            <input name="keywords" type="text" class="form-control" placeholder="' + self.name + '">')
        renderer.append('            <span class="input-group-btn">')
        renderer.append('                <button class="btn btn-default" type="submit">' + self.button_name.render() + '</button>')
        renderer.append('            </span>')
        renderer.append('        </div>')
        renderer.append('    </div>')
        renderer.append('</form>')


class Parallax(Object):
    def __init__(self, background_url='', items=Default, speed=3, **kwargs):
        self.init(kwargs)
        self.background_url = self.param(background_url, UrlParam, 'URL to the background image')
        self.items = self.param(items, ObjectsParam, 'The items in the section', Objects())
        self.speed = self.param(speed, FloatParam, 'The speed of the parallax, higher numbers is slower. 1 is normal page speed, 2 is half speed, etc.')
        self.add_style('background: url({}) 50% 0/100% fixed; height: auto; margin: 0 auto; width: 100%; position: relative;'.format(self.background_url))
        self.id_needed()

    def get_html(self, renderer):
        renderer.append('<section' + self.base_attributes + '>')
        renderer.render('    ', self.items)
        renderer.append('</section>')

        renderer.append_js("var scroll = $('#" + self.id + "'); $(window).scroll(function() {scroll.css({ backgroundPosition: '50% ' + (-($(window).scrollTop() / " + str(self.speed) + ")) + 'px' })});")


class Feature(Object):
    def __init__(self, heading=None, explanation=None, demonstration=None, flipped=False, **kwargs):
        self.init(kwargs)
        self.heading = self.param(heading, ObjectsParam, 'Heading for the feature')
        self.explanation = self.param(explanation, ObjectsParam, 'Explanation of the feature')
        self.demonstration = self.param(demonstration, ObjectsParam, 'Something to demonstrate the feature, such as an image')
        self.flipped = self.param(flipped, BooleanParam, 'Flip the explanation and demonstation. It looks good to alternate between features.')

    def get_html(self, renderer):
        def explanation():
            renderer.append('        <hr class="{}">'.format(renderer.add_css_class('float: left;width: 200px;border-top: 3px solid #e7e7e7;')))
            renderer.append('        <div class="clearfix"></div>')
            renderer.append('        <h2>')
            renderer.render('            ', self.heading)
            renderer.append('        </h2>')
            renderer.append('        <p class="lead">')
            renderer.render('            ', self.explanation)
            renderer.append('        </p>')

        def demonstration():
            renderer.render('        ', self.demonstration)


        renderer.append('<div class="row">')
        renderer.append('    <div class="col-lg-5 col-sm-6">')
        demonstration() if self.flipped else explanation()
        renderer.append('    </div>')
        renderer.append('    <div class="col-lg-5 col-lg-offset-2 col-sm-6">')
        explanation() if self.flipped else demonstration()
        renderer.append('    </div>')
        renderer.append('</div>')

