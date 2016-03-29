from shark.base import BaseObject
from shark.resources import Resources


class StarRating(BaseObject):
    def __init__(self, rating=None, readonly=False, **kwargs):
        self.init(kwargs)
        self.rating = self.param(rating, 'int', 'Current rating.')
        self.readonly = self.param(readonly, 'bool', 'Is the rating read only?')
        self.id_needed = True

    def get_html(self, html):
        html.append('<select' + self.base_attributes + '>')
        for i in range(1, 6):
            html.append('   <option value="{}"{}>{}</option>'.format(i, ' selected' if i==self.rating else '', i))
        html.append('</select>')

        html.append_js('$("#{}").barrating({{theme: "bootstrap-stars"{}}});'.format(self.id, ', readonly: true' if self.readonly else ''))

        html.add_resource('/static/shark/js/jquery.barrating.min.js', 'js', 'star_rating', 'main')
        html.add_resource('/static/shark/css/rating-themes/bootstrap-stars.css', 'css', 'star_rating', 'bootstrap')
