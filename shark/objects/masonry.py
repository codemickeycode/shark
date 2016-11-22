from django.db.models import Model
from shark.base import BaseObject, Default


class Masonry(BaseObject):
    """
    Render a masonry grid using the masonry js library (http://masonry.desandro.com/)
    """
    def __init__(self, items=Default, columnwidth="col-md-4", **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'The items', [])
        self.columnwidth = self.param(columnwidth, 'string', 'Bootstrap class for the column witdh')
        self.id_needed()
        self.add_class('grid')

    def get_html(self, renderer):
        renderer.add_resource('//unpkg.com/masonry-layout@4.1.1/dist/masonry.pkgd.min.js', 'js', 'masonry', 'main')
        renderer.add_resource('//npmcdn.com/imagesloaded@4.1/imagesloaded.pkgd.min.js', 'js', 'imagesloaded', 'main')

        renderer.append('<div class="container-fluid">')
        renderer.append('    <div' + self.base_attributes + '>')
        renderer.append('        <div class="grid-sizer ' + self.columnwidth + '"></div>')
        renderer.render('        ', self.items)
        renderer.append('    </div>')
        renderer.append('</div>')

        renderer.append_js('$("#{}").masonry({{itemSelector: ".grid-item", columnWidth: ".grid-sizer", percentPosition: true}});'.format(self.id))
        renderer.append_js('$("#{}").imagesLoaded().progress( function() {{ $("#{}").masonry("layout");}});'.format(self.id, self.id))


class MasonryItem(BaseObject):
    """
    Render an item in a masonry grid
    """
    def __init__(self, items=Default, columnwidth="col-md-4", **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'The content of the item')
        self.columnwidth = self.param(columnwidth, 'string', 'Bootstrap class for the column witdh')
        self.add_class('grid-item')
        self.add_class(self.columnwidth)

    def get_html(self, renderer):
        renderer.append('<div' + self.base_attributes + '>')
        renderer.append('    <div class="grid-item-content">')
        renderer.render('        ', self.items)
        renderer.append('    </div>')
        renderer.append('</div>')